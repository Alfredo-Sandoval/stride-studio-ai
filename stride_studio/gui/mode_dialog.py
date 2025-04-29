#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  stride_studio/gui/mode_dialog.py  –  pick Video-file vs Live-stream
# ---------------------------------------------------------------------------
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QLabel, QVBoxLayout


class ModeDialog(QDialog):
    """Returns True for live-stream, False for video-file, None on cancel."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Choose input mode")
        self.setModal(True)
        self._choice: bool | None = None  # None = cancelled

        # ----- layout -----------------------------------------------------
        main = QVBoxLayout(self)
        main.addWidget(
            QLabel(
                "How would you like to start Stride Studio?", alignment=Qt.AlignCenter
            )
        )

        row = QHBoxLayout()
        vid_btn = QPushButton("📂 Video file")
        live_btn = QPushButton("🎥 Live camera")

        vid_btn.clicked.connect(lambda: self._select(False))
        live_btn.clicked.connect(lambda: self._select(True))

        row.addWidget(vid_btn)
        row.addWidget(live_btn)
        main.addLayout(row)

    # ---------------------------------------------------------------------
    def _select(self, live: bool):
        self._choice = live
        self.accept()

    # public API
    def exec_choice(self) -> bool | None:
        return self.exec() and self._choice
