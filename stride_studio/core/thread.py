#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  stride_studio_ai/core/thread.py  –  background inference + optional export
#  2025-04-30  (full, unabridged)
# ---------------------------------------------------------------------------
from __future__ import annotations

import cv2, gc, logging, time
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QThread, QObject, Signal, QMutex, QWaitCondition
from PySide6.QtGui import QImage, QPixmap
from ultralytics import YOLO

log = logging.getLogger("stride_studio.core.thread")


# --------------------------------------------------------------------------- #
class VideoProcessingThread(QThread):
    """
    Worker that

    * reads frames between *start_frame* and *end_frame* OR from live feed
    * rotates if required
    * runs the model (wrapper **or** raw `ultralytics.YOLO`)
    * emits live preview via ``change_pix``
    * stores every annotated frame so :meth:`save_video` can be called later
    """

    # Qt signals
    change_pix = Signal(QPixmap)  # live preview
    progress = Signal(int)  # 0-100
    finished_ok = Signal(str)  # final status

    # --------------------------------------------------------------------- #
    def __init__(
        self,
        model: Any,  # wrapper or raw YOLO
        *,
        input_path: str | Path | None = None,
        live_capture: cv2.VideoCapture | None = None,
        start_frame: int = 0,
        end_frame: int = -1,
        rotation_angle: int = 0,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.model = model
        self.path = str(input_path) if input_path else ""
        self.cap = live_capture
        self.frame_start = max(0, start_frame)
        self.frame_end = end_frame
        self.rotation_angle = rotation_angle
        self.live_mode = live_capture is not None

        # populated in run() or from live_capture
        self.total = 0
        self.fps = 30.0

        self.current_frame = 0
        self._run_flag = True

        self.processed_frames: list[np.ndarray] = []  # for save_video()

        # mutex/cond → pause / resume (GUI slider drag)
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self._pause = False

    def prepare(self) -> bool:
        """Prepare the video capture source."""
        if self.cap is None:  # Open file only if not in live mode
            self.cap = cv2.VideoCapture(self.path)
            if not self.cap.isOpened():
                log.error("Failed to open video file: %s", self.path)
                return False
            self.total = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        else:  # Live mode
            self.total = int(1e9)  # Effectively infinite for live stream
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0

        if self.frame_end < 0 or self.frame_end > self.total:
            self.frame_end = self.total

        if not self.live_mode:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_start)
        self.current_frame = self.frame_start
        return True

    # ────────────────────────── helpers ───────────────────────────────── #
    @staticmethod
    def _pm_from_bgr(arr: np.ndarray) -> QPixmap:
        h, w = arr.shape[:2]
        return QPixmap.fromImage(QImage(arr.data, w, h, 3 * w, QImage.Format_BGR888))

    def _apply_rotation(self, fr: np.ndarray) -> np.ndarray:
        rot = self.rotation_angle % 360
        if rot == 90:
            return cv2.rotate(fr, cv2.ROTATE_90_CLOCKWISE)
        elif rot == 180:
            return cv2.rotate(fr, cv2.ROTATE_180)
        elif rot == 270:
            return cv2.rotate(fr, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return fr

    def _infer_and_annotate(self, bgr: np.ndarray) -> np.ndarray:
        """
        Accepts either:

        * our lightweight wrapper (callable → BGR ndarray)
        * a raw ``ultralytics.YOLO`` model
        """
        if not isinstance(self.model, YOLO):
            # wrapper already returns BGR
            return self.model(bgr)

        # raw YOLO object
        res = self.model(bgr, verbose=False)[0]
        plotted = res.plot()
        return plotted if isinstance(plotted, np.ndarray) else bgr

    # ─────────────────────────── public slots ────────────────────────────
    def pause(self):
        self.mutex.lock()
        self._pause = True
        self.mutex.unlock()

    def resume(self):
        self.mutex.lock()
        self._pause = False
        self.mutex.unlock()
        self.cond.wakeAll()

    # ─────────────────────────── QThread.run ─────────────────────────────
    def run(self) -> None:
        if not self.prepare():
            self.finished_ok.emit("Cannot open video source.")
            return

        try:
            while self._run_flag and self.current_frame < self.frame_end:
                # handle pause ------------------------------------------
                self.mutex.lock()
                while self._pause:
                    self.cond.wait(self.mutex)
                self.mutex.unlock()

                ok, raw = self.cap.read()
                if not ok:
                    if self.live_mode:
                        # In live mode, wait a bit and try again
                        time.sleep(0.01)
                        continue
                    else:
                        log.warning("Early EOF")
                        break

                raw = self._apply_rotation(raw)
                annotated = self._infer_and_annotate(raw)

                # buffer + preview
                if not self.live_mode:
                    self.processed_frames.append(annotated.copy())

                self.change_pix.emit(self._pm_from_bgr(annotated))

                if not self.live_mode:
                    pct = int(
                        100
                        * (self.current_frame - self.frame_start)
                        / max(1, self.frame_end - self.frame_start)
                    )
                    self.progress.emit(pct)
                else:
                    # Live mode doesn't have fixed progress
                    self.progress.emit(50)  # Or some other indicator

                self.current_frame += 1

        except Exception as e:
            log.exception("Thread error")
            self.finished_ok.emit(f"Error: {e}")
        finally:
            if not self.live_mode and self.cap:  # Only release if opened by this thread
                self.cap.release()
            gc.collect()
            self.finished_ok.emit("Processing complete.")

    # ─────────────────────────── save video ──────────────────────────────
    def save_video(self, out_path: str, fourcc: str = "FFV1") -> tuple[bool, str]:
        if not self.processed_frames:
            return False, "No frames processed."

        h, w = self.processed_frames[0].shape[:2]
        writer = cv2.VideoWriter(
            out_path, cv2.VideoWriter_fourcc(*fourcc), self.fps, (w, h)
        )
        if not writer.isOpened():
            return False, f"Cannot write {out_path}"

        for fr in self.processed_frames:
            writer.write(fr)
        writer.release()
        return True, f"Saved → {out_path}"
