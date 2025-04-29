# utils/theme.py – Dark UI styling for Stride Studio
"""Centralised UI theme helper.

* Applies a dark palette to **all** Qt widgets.
* Adds a stylesheet so **QPushButton** widgets give instant visual feedback:
  - normal -> dark slate grey (#42464e)
  - hover -> green (success) (#2e7d32)
  - pressed -> red (danger) (#c62828)
  - disabled -> greyed-out

Usage
-----
>>> from PySide6.QtWidgets import QApplication
>>> from stride_studio.utils.theme import apply_dark_theme
>>> app = QApplication([])
>>> apply_dark_theme(app)
"""

from __future__ import annotations

import logging
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QIcon
from PySide6.QtWidgets import QApplication

# package‑scoped logger (configured in utils.logger.init)
log = logging.getLogger("stride_studio.theme")

# --------------------------------------------------------------------------- #
# Modern color palette
DARK_BG = QColor(22, 27, 34)  # Main window/background (darker GitHub-like)
BASE_BG = QColor(13, 17, 23)  # Text entry/list backgrounds (even darker)
ACCENT = QColor(88, 166, 255)  # Primary accent (GitHub blue)
SECONDARY = QColor(121, 184, 255)  # Secondary accent
SUCCESS = QColor(46, 160, 67)  # Success green
DANGER = QColor(248, 81, 73)  # Danger/error red
WARNING = QColor(255, 180, 0)  # Warning/caution yellow

# --------------------------------------------------------------------------- #


def dark_theme(app: QApplication) -> None:
    """Apply the dark palette and enhanced button stylesheet to *app*."""
    log.debug("Applying dark theme …")

    pal = QPalette()
    for role, col in [
        (QPalette.Window, DARK_BG),
        (QPalette.WindowText, Qt.white),
        (QPalette.Base, BASE_BG),
        (QPalette.AlternateBase, DARK_BG),
        (QPalette.ToolTipBase, Qt.white),
        (QPalette.ToolTipText, Qt.white),
        (QPalette.Text, Qt.white),
        (QPalette.Button, DARK_BG),
        (QPalette.ButtonText, Qt.white),
        (QPalette.Highlight, ACCENT),
        (QPalette.HighlightedText, Qt.black),
    ]:
        pal.setColor(role, col)

    app.setPalette(pal)
    log.debug("Setting application icon from Stride Studio icon")
    icon_path = os.path.join(
        os.path.dirname(__file__), "..", "gui", "icons", "icon.ico"
    )
    app.setWindowIcon(QIcon(icon_path))
    if not app.windowIcon().isNull():
        log.debug(f"Icon set successfully from {icon_path}")
    else:
        log.error(f"Failed to set icon from {icon_path}: file not found or invalid")

    # ----- widgets stylesheet (enhanced modern look) ------------------------- #
    app.setStyleSheet(
        """
        /* Main window styling */
        QMainWindow, QDialog {
            background-color: #16171b;
            color: #e1e4e8;
        }
        
        /* App title styling */
        QLabel#AppTitle {
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
        }
        
        /* Drop area with improved styling */
        QLabel#DropArea {
            border: 1px solid #30363d;
            border-radius: 8px;
            background-color: #1a1d24;
            color: #8b949e;
            font-size: 16px;
            padding: 20px;
        }
        
        /* Button styling with modern look */
        QPushButton {
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 32px;
        }
        QPushButton:hover {
            background-color: #30363d;
            border-color: #8b949e;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #0d419d;
            border-color: #58a6ff;
        }
        QPushButton:disabled {
            background-color: #21262d;
            color: #484f58;
            border: 1px solid #21262d;
        }
        
        /* Slider styling for better UX */
        QSlider::groove:horizontal {
            border: 1px solid #30363d;
            height: 8px;
            background: #0d1117;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #58a6ff;
            border: 1px solid #388bfd;
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #79b8ff;
            border: 1px solid #79b8ff;
        }
        
        /* Progress bar with solid color */
        QProgressBar {
            border: 1px solid #30363d;
            border-radius: 5px;
            background-color: #0d1117;
            text-align: center;
            color: white;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #58a6ff;
            border-radius: 5px;
        }
        
        /* Line edit fields */
        QLineEdit {
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 5px 10px;
            background-color: #0d1117;
            color: #c9d1d9;
            selection-background-color: #388bfd;
        }
        QLineEdit:focus {
            border: 1px solid #58a6ff;
        }
        
        /* Checkbox styling */
        QCheckBox {
            color: #c9d1d9;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #30363d;
        }
        QCheckBox::indicator:unchecked {
            background-color: #0d1117;
        }
        QCheckBox::indicator:checked {
            background-color: #388bfd;
            image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='24' height='24'><path fill='%23ffffff' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>");
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #161b22;
            color: #8b949e;
            border-top: 1px solid #30363d;
        }
        """
    )

    log.debug("Dark theme applied.")
