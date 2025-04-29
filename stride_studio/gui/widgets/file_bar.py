from __future__ import annotations
import datetime, pathlib
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QStyle,
    QComboBox,
)


class FileBar(QWidget):
    """Load/Save controls."""

    open_video = Signal()
    save_video = Signal(str)  # Emits desired filename prefix

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins for the bar itself

        self.load_btn = QPushButton("Load Video")
        self.load_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.load_btn.clicked.connect(self.open_video)
        self.load_btn.setMinimumWidth(120)
        layout.addWidget(self.load_btn)
        layout.addSpacing(10)

        save_box = QHBoxLayout()  # Inner layout for save button + edit
        self.save_btn = QPushButton("Save Video")
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumWidth(120)
        self.save_btn.clicked.connect(
            lambda: self.save_video.emit(self.out_edit.text())
        )
        save_box.addWidget(self.save_btn)

        self.out_edit = QLineEdit(placeholderText="Output filename (optional)")
        self.out_edit.setMinimumWidth(300)
        save_box.addWidget(self.out_edit)

        # Add format combo here as it relates to saving
        save_box.addSpacing(10)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "AVI", "MKV"])
        self.format_combo.setFixedWidth(80)
        save_box.addWidget(self.format_combo)

        save_wrap = QWidget()
        save_wrap.setLayout(save_box)
        layout.addWidget(save_wrap)

    # ------------------------------------------------------------------
    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select video", "", "Video (*.mp4 *.avi *.mov *.mkv *.wmv)"
        )
        if path:
            self.open_video.emit(path)

    def _save_file(self):
        name = self.out_edit.text().strip()
        if not name:
            ts = datetime.datetime.now().strftime("%H%M%S")
            name = f"annotated_{ts}.mkv"
        self.save_video.emit(name)
