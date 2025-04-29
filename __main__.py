#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  stride_studio/__main__.py  –  unified entry-point
# ---------------------------------------------------------------------------
from __future__ import annotations

import logging
import sys
from pathlib import Path
import time

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

# ── ensure repo root is on PYTHONPATH --------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

# ── local imports ----------------------------------------------------------
from stride_studio.utils.logger import init as init_logger
from stride_studio.utils.theme import dark_theme
from stride_studio.gui.splash_screen import StrideStudioSplash
from stride_studio.gui.mode_dialog import ModeDialog
from stride_studio.gui.main_window import MainWindow

# ---------------------------------------------------------------------------
SPLASH_MS = 2000  # how long the logo stays up (ms)
logger = init_logger(logging.INFO)  # global logger early


def main() -> None:
    app = QApplication(sys.argv)
    dark_theme(app)

    splash = StrideStudioSplash(app)
    splash.show()
    # Allow splash to be visible for a short time, process events
    start_time = time.time()
    while time.time() - start_time < 1.5:  # Show for 1.5 seconds
        app.processEvents()
        time.sleep(0.02)

    # Explicitly hide splash BEFORE showing the modal dialog
    splash.hide()
    app.processEvents()
    # Clean up splash resources immediately after hiding
    splash.deleteLater()

    # Determine mode now that splash is hidden
    dialog = ModeDialog()
    dialog.setWindowModality(Qt.ApplicationModal)  # Make it properly modal
    dialog.setWindowFlag(Qt.WindowStaysOnTopHint)  # Keep it on top
    pick = dialog.exec_choice()  # True = live, False = video, None = cancel

    if pick is None:
        logger.info("Mode selection cancelled, exiting.")
        # No main window created, just exit
        return

    logger.info("Mode selected: %s", "Live" if pick else "Video")

    # Create and show the main window *after* mode is chosen
    main_win = MainWindow(live=pick)
    main_win.show()

    sys.exit(app.exec())


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
