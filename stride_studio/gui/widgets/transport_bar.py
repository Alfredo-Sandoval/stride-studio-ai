from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QComboBox,
    QLabel,
    QStyle,
)


class TransportBar(QWidget):
    """Play / seek / speed / rotate bar."""

    play = Signal()
    pause = Signal()
    prev = Signal()
    next = Signal()
    seek = Signal(int)
    speed = Signal(float)
    rotate = Signal()

    # ------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setSpacing(8)

        def _btn(icon: QStyle.StandardPixmap, sig: Signal):
            b = QPushButton()
            b.setIcon(self.style().standardIcon(icon))
            b.setFixedWidth(34)
            b.clicked.connect(sig)  # type: ignore[arg-type]
            lay.addWidget(b)
            return b

        _btn(QStyle.SP_MediaSkipBackward, self.prev)
        _btn(QStyle.SP_MediaSeekBackward, self.prev)

        self._play = QPushButton("Play")
        self._play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self._play.setMinimumWidth(90)
        self._play.clicked.connect(self._toggle)
        lay.addWidget(self._play)

        _btn(QStyle.SP_MediaSeekForward, self.next)
        _btn(QStyle.SP_MediaSkipForward, self.next)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderReleased.connect(lambda: self.seek.emit(self.slider.value()))
        lay.addWidget(self.slider, 1)

        lay.addWidget(QLabel("Speed:"))
        self.speed_box = QComboBox()
        self.speed_box.addItems(
            ["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"]
        )
        self.speed_box.setCurrentIndex(3)
        self.speed_box.currentTextChanged.connect(
            lambda t: self.speed.emit(float(t.rstrip("x")))
        )
        self.speed_box.setFixedWidth(72)
        lay.addWidget(self.speed_box)

        self._rot = QPushButton("Rotate")
        self._rot.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self._rot.clicked.connect(self.rotate)  # type: ignore[arg-type]
        lay.addWidget(self._rot)

    # ------------------------------------------------------------------ helpers
    def set_playing(self, playing: bool):
        icon = QStyle.SP_MediaPause if playing else QStyle.SP_MediaPlay
        self._play.setIcon(self.style().standardIcon(icon))
        self._play.setText("Pause" if playing else "Play")

    def _toggle(self):
        (self.pause if self._play.text() == "Pause" else self.play).emit()
