#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# stride_studio/gui/main_window.py – compact front-end for Stride-Studio-AI
# 2025-04-30  ·  supports video-file + live-cam, model hot-swap, saving
# ---------------------------------------------------------------------------
from __future__ import annotations

# ── std-lib ──────────────────────────────────────────────────────────────
import datetime, logging
from pathlib import Path
from typing import Optional

# ── third-party ──────────────────────────────────────────────────────────
import cv2
from PySide6.QtCore import Qt, QTimer, Slot, Signal, QSize
from PySide6.QtGui import QCloseEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QStyle,
    QMainWindow,
    QPushButton,
    QSlider,
    QSizePolicy,
    QCheckBox,
    QLineEdit,
    QProgressBar,
)

# ── local ────────────────────────────────────────────────────────────────
from ..core.thread import (
    VideoProcessingThread,
)  # pylint: disable=import-error
from ..core.models import (
    YoloPose,
    YoloGeneric,
)  # pylint: disable=import-error
from ..utils.logger import get_logger  # pylint: disable=import-error
from ..utils.theme import dark_theme  # pylint: disable=import-error

# Import widgets
from .widgets import VideoView, TransportBar, FileBar

log = get_logger("stride_studio.gui.main_window")

# ---------------------------------------------------------------------------

_TASK2CKPT = {
    "Pose": "yolo11x-pose.pt",
    "Detection": "yolo11x.pt",
    "Segmentation": "yolo11x-seg.pt",
    "Classification": "yolo11x-cls.pt",
    "OrientedBBox": "yolo11x-obb.pt",
}

SUP_EXT = (".mp4", ".avi", ".mov", ".mkv", ".wmv")

# ---------------------------------------------------------------------------


class MainWindow(QMainWindow):
    """Controller that glues together widgets + processing logic."""

    def __init__(self, *, live: bool = False):
        super().__init__()
        self.setWindowTitle("Stride Studio")
        self.resize(1024, 720)

        # ---------- widgets ------------------------------------------------
        self._build_ui()

        # ---------- run-time state ----------------------------------------
        self.live_mode = live
        self.selected_cam = 0
        self.cap: Optional[cv2.VideoCapture] = None
        self.thread: Optional[VideoProcessingThread] = None
        self.yolo_model = None
        self.video_loaded = False
        self.is_playing = False
        self.fps = 30.0
        self.cur_frame = 0
        self.tot_frames = 0
        self.rotation = 0
        self.speed = 1.0
        self.video_path: str | None = None

        # playback timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

        # ---------- signal wiring -----------------------------------------
        self.transport.play.connect(self._play)
        self.transport.pause.connect(self._pause)
        self.transport.prev.connect(lambda: self._seek_rel(-1))
        self.transport.next.connect(lambda: self._seek_rel(+1))
        self.transport.seek.connect(self._seek_abs)
        self.transport.speed.connect(self._set_speed)
        self.transport.rotate.connect(self._rotate)

        self.files.open_video.connect(self.load_video)
        self.files.save_video.connect(self._save_video)

        self.model_combo.currentIndexChanged.connect(self._change_model)

        # auto-live prompt
        if self.live_mode:
            QTimer.singleShot(100, self._open_camera)
        else:
            QTimer.singleShot(300, self._initial_prompt)

    def _populate_models(self) -> None:
        """Populate the model selection combobox."""
        self.model_combo.addItems(list(_TASK2CKPT.keys()))

    def _change_model(self) -> None:
        """Handle model selection change: stop old thread, start new one."""
        log.info(f"Model selection changed to: {self.model_combo.currentText()}")

        # Stop the current processing thread if it's running
        if self.thread and self.thread.isRunning():
            log.info("Stopping current processing thread for model change...")
            # Use a similar stopping mechanism as _cleanup_all
            self.thread.requestInterruption()  # Signal the thread to stop
            if not self.thread.wait(3000):  # Wait up to 3 seconds
                log.warning("Processing thread did not stop gracefully. Terminating.")
                self.thread.terminate()  # Force stop if necessary
                self.thread.wait()  # Wait again after terminate
            else:
                log.info("Previous processing thread stopped.")
            self.thread = None  # Clear the reference

        # Start processing with the new model
        # Ensure video/camera is still loaded before restarting
        if self.video_loaded:
            self._start_processing()  # No auto=True needed, user explicitly changed model
        else:
            log.info("No video/camera loaded, model change deferred until loaded.")

    def _build_ui(self) -> None:
        # Central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ––– model selection –––––––––––––––––––––––––––––––––––
        model_cfg = QHBoxLayout()
        model_cfg.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self._populate_models()
        model_cfg.addWidget(self.model_combo)
        model_cfg.addStretch()
        main_layout.addLayout(model_cfg)

        # ––– video display (using VideoView widget) ––––––––––––––––––––––––––
        self.view = VideoView()
        self.view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        main_layout.addWidget(self.view, 1)

        # ––– transport bar (using TransportBar widget) ––––––––––––––––––––––
        self.transport = TransportBar()
        main_layout.addWidget(self.transport)

        # ––– file actions (using FileBar widget) –––––––––––––––––––––––––––––
        self.files = FileBar()
        main_layout.addWidget(self.files)

        # Connect signals from widgets
        self.transport.play.connect(
            self.toggle_play_pause
        )  # Assuming play signal handles toggle
        self.transport.seek.connect(
            self._seek
        )  # Assuming seek signal emits absolute frame
        self.transport.speed_changed.connect(
            self._change_speed
        )  # Assuming speed signal emits float
        self.transport.rotated.connect(self._rotate)  # Assuming rotate signal exists
        self.transport.next_frame.connect(self._next)  # Assuming next signal exists
        self.transport.prev_frame.connect(self._previous)  # Assuming prev signal exists
        self.transport.rewind.connect(self._rewind)  # Assuming rewind signal exists
        self.transport.fast_forward.connect(
            self._fast_forward
        )  # Assuming ff signal exists
        self.transport.slider_pressed.connect(
            lambda: self.thread and self.thread.pause()
        )
        self.transport.slider_released.connect(lambda: self._resume_thread_if_paused())

        self.files.open_video.connect(
            self.load_video
        )  # Assuming open signal has no args
        self.files.save_video.connect(
            self._save_video_clicked
        )  # Assuming save signal has prefix arg

        self.statusBar().showMessage("Ready.")
        self._reset_ui()

    def _resume_thread_if_paused(self):
        # When slider is released, resume thread if it was paused by slider press
        # Check if thread exists and if it might have been paused by the slider action
        if (
            self.thread
        ):  # and self.thread.isPausedBySlider(): # Need thread state tracking
            self.thread.resume()

    # ───────────────────────────────── video / camera ────────────────────
    def load_video(self, path: str):
        self._cleanup_all()

        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", f"Cannot open {path}")
            return

        self.video_path = path
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.tot_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_loaded = True
        self.cur_frame = 0
        ok, frame = self.cap.read()
        if not ok:
            QMessageBox.critical(self, "Error", "Cannot read first frame")
            return

        self.view.show(frame)
        self.transport.slider.setMaximum(max(0, self.tot_frames - 1))
        self._ui_state()
        log.info("Loaded video %s", Path(path).name)

    # ---------- live cam --------------------------------------------------
    def _open_camera(self) -> bool:
        self._cleanup_all()
        cam_idx = self.selected_cam
        log.info(f"Attempting to open webcam index {cam_idx}...")
        # Try DSHOW first
        self.cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            log.warning(f"Cannot open webcam index {cam_idx} using DSHOW.")
            # Try default backend
            log.info(f"Retrying webcam index {cam_idx} with auto-backend...")
            self.cap = cv2.VideoCapture(cam_idx)
            if not self.cap.isOpened():
                log.error(f"Cannot open webcam index {cam_idx} with any backend.")
                QMessageBox.critical(
                    self,
                    "Camera Error",
                    f"Cannot open webcam {cam_idx}. Ensure it's not in use.",
                )
                return False

        log.info(f"Webcam index {cam_idx} opened successfully.")
        self.video_loaded = True
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.tot_frames = int(1e9)  # effectively "unknown"
        self.cur_frame = 0
        ok, frame = self.cap.read()
        if ok and frame is not None:
            self.view.show(frame)
        else:
            log.warning("Failed to read initial frame from webcam.")
            # Proceed anyway?

        self.transport.slider.setEnabled(False)  # no seeking in live
        self.files.load_btn.setEnabled(False)  # Disable loading video in live mode
        self._update_time()
        self._ui_state()
        # Don't auto-start playback here, wait for user/processing
        # Start processing immediately after opening the camera
        self._start_processing(auto=True)
        return True

    # ─────────────────────────── playback / seek ─────────────────────────
    def _play(self):
        if not self.video_loaded:
            return
        self.is_playing = True
        self.timer.start(int(1000 / (self.fps * self.speed)))
        self.transport.set_playing(True)

    def _pause(self):
        self.is_playing = False
        self.timer.stop()
        self.transport.set_playing(False)

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.is_playing:
            self._pause()
        else:
            self._play()

    def _tick(self):
        ok, frame = self.cap.read() if self.cap else (False, None)
        if not ok:
            self._pause()
            return
        self.cur_frame += 1
        self.view.show(frame, self.rotation)
        self.transport.slider.setValue(self.cur_frame)

    def _seek_abs(self, pos: int):  # files only
        if self.live_mode or not self.cap:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        self.cur_frame = pos
        ok, frame = self.cap.read()
        if ok:
            self.view.show(frame, self.rotation)

    def _seek_rel(self, delta: int):
        self._seek_abs(max(0, self.cur_frame + delta))

    def _set_speed(self, s: float):
        self.speed = s
        if self.is_playing:
            self.timer.start(int(1000 / (self.fps * self.speed)))

    def _rotate(self):
        self.rotation = (self.rotation + 90) % 360

    # ───────────────────────── processing thread ─────────────────────────
    def _start_processing(self, *, auto=False):
        if auto and not self.video_loaded:
            return
        if self.thread and self.thread.isRunning():
            return

        # load model
        task = self.model_combo.currentText()
        ckpt = _TASK2CKPT[task]
        try:
            from ultralytics import YOLO

            model_path = Path(__file__).resolve().parent.parent / "models" / ckpt
            wrapper = YoloPose if YOLO(str(model_path)).task == "pose" else YoloGeneric
            self.yolo_model = wrapper(ckpt)
        except Exception as e:
            QMessageBox.critical(self, "Model", str(e))
            return

        # rewind file for full pass
        if not self.live_mode and self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.thread = VideoProcessingThread(
            model=self.yolo_model,
            input_path=None if self.live_mode else self.video_path,
            live_capture=self.cap if self.live_mode else None,
            rotation_angle=self.rotation,
            parent=self,
        )
        self.thread.change_pix.connect(
            lambda pm: self.view.setPixmap(
                pm.scaled(self.view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        )
        self.thread.progress.connect(self.transport.slider.setValue)
        self.thread.finished_ok.connect(self._on_done)
        self.thread.start()
        self.files.save_btn.setEnabled(False)
        log.info("Processing started (%s)", task)

    @Slot(str)
    def _on_done(self, msg: str):
        log.info(msg)
        self.files.save_btn.setEnabled(
            bool(self.thread and self.thread.processed_frames)
        )

    # ───────────────────────────── saving ────────────────────────────────
    def _save_video(self, name: str):
        if not (self.thread and self.thread.processed_frames):
            QMessageBox.information(self, "Save", "Run processing first")
            return
        out = QFileDialog.getSaveFileName(
            self, "Save", name, "Matroska (*.mkv);;AVI (*.avi);;MP4 (*.mp4)"
        )[0]
        if not out:
            return
        ok, msg = self.thread.save_video(
            out, fourcc="FFV1" if out.lower().endswith(".mkv") else "XVID"
        )
        QMessageBox.information(self, "Save", msg if ok else f"Failed: {msg}")

    # ──────────────────────────── prompts ────────────────────────────────
    def _initial_prompt(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose video", "", "Video (*.mp4 *.avi *.mov *.mkv *.wmv)"
        )
        if path:
            self.load_video(path)
            self._prompt_task_then_process()

    def _prompt_task_then_process(self):
        task, ok = QInputDialog.getItem(
            self, "Task", "Select model task:", list(_TASK2CKPT), 0, False
        )
        if ok:
            self.model_combo.setCurrentText(task)
            self._start_processing()

    # ───────────────────────── housekeeping ─────────────────────────────
    def _ui_state(self):
        processing = self.thread and self.thread.isRunning()
        # Enable camera combo only in live mode AND when not processing
        self.files.camera_combo.setEnabled(
            self.live_mode and not processing and bool(self.available_cameras)
        )

        play_en = self.video_loaded and not processing
        # Disable transport controls if in live mode and processing
        # Allow play/pause if live mode and *not* processing (for preview)
        live_preview_mode = self.live_mode and not processing

        self.transport.play_btn.setEnabled(play_en or live_preview_mode)
        # Seek/skip buttons always disabled in live mode
        self.transport.slider.setEnabled(play_en and not self.live_mode)
        self.transport.prev_btn.setEnabled(play_en and not self.live_mode)
        self.transport.next_btn.setEnabled(play_en and not self.live_mode)
        self.transport.rew_btn.setEnabled(play_en and not self.live_mode)
        self.transport.ff_btn.setEnabled(play_en and not self.live_mode)

        # Save button only for non-live video after processing
        self.files.save_btn.setEnabled(
            (not self.live_mode)
            and self.video_loaded
            and not processing
            and bool(self.thread and self.thread.processed_frames)
        )
        # Load button disabled in live mode or during processing
        self.files.load_btn.setEnabled(not self.live_mode and not processing)
        # Other general controls disabled during processing
        self.model_combo.setEnabled(not processing)
        self.files.format_combo.setEnabled(not processing)
        self.files.out_edit.setEnabled(not processing)
        self.transport.rot_btn.setEnabled(self.video_loaded and not processing)
        self.transport.speed_combo.setEnabled(self.video_loaded and not processing)

        # Update play button icon based on actual playback state
        self.transport.play_btn.setIcon(
            self.style().standardIcon(
                QStyle.SP_MediaPause if self.is_playing else QStyle.SP_MediaPlay
            )
        )

    def _cleanup_all(self):
        self.timer.stop()
        self.is_playing = False
        if self.thread and self.thread.isRunning():
            log.info("Requesting processing thread interruption...")
            self.thread.requestInterruption()
            if not self.thread.wait(3000):  # Wait max 3 seconds
                log.warning("Processing thread did not finish gracefully. Terminating.")
                self.thread.terminate()  # Force termination if wait fails
                self.thread.wait()  # Wait again after terminate
            else:
                log.info("Processing thread finished.")

        self.thread = None
        if self.cap:
            log.info("Releasing video capture...")
            self.cap.release()
            self.cap = None
        self.video_loaded = False
        log.info("Cleanup complete.")

    def closeEvent(self, e: QCloseEvent):
        self._cleanup_all()
        e.accept()

    # drag-n-drop ---------------------------------------------------------
    def dragEnterEvent(self, e):
        e.acceptProposedAction() if e.mimeData().hasUrls() else None

    def dropEvent(self, e: QDropEvent):
        url = e.mimeData().urls()
        if url and url[0].toLocalFile().lower().endswith(SUP_EXT):
            self.load_video(url[0].toLocalFile())


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    app = QApplication(sys.argv)
    win = MainWindow()  # pass live=True for webcam mode
    win.show()
    sys.exit(app.exec())
