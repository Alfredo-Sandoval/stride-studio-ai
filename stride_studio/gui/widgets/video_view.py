from __future__ import annotations
import cv2, numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class VideoView(QLabel):
    """QLabel that can display raw BGR numpy frames."""

    def __init__(self, text: str = "No video"):
        super().__init__(text, alignment=Qt.AlignCenter)
        self.setScaledContents(False)

    # ------------------------------------------------------------------ api
    def show(self, frame_bgr: np.ndarray, rotate: int = 0):
        if frame_bgr is None or frame_bgr.size == 0:
            return
        if rotate:
            frame_bgr = cv2.rotate(
                frame_bgr,
                {
                    90: cv2.ROTATE_90_CLOCKWISE,
                    180: cv2.ROTATE_180,
                    270: cv2.ROTATE_90_COUNTERCLOCKWISE,
                }[rotate],
            )
        h, w, c = frame_bgr.shape
        qimg = QImage(frame_bgr.data, w, h, c * w, QImage.Format_BGR888)
        pm = QPixmap.fromImage(qimg)
        self.setPixmap(
            pm.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def clear(self, text="No video"):
        self.setText(text)
        self.setPixmap(QPixmap())
