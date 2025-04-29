#!/usr/bin/env python3
# Test script for the splash screen with direct imports

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Direct import from the local file
from gui.splash_screen import StrideStudioSplash


def main():
    app = QApplication(sys.argv)
    splash = StrideStudioSplash(app)
    splash.show()

    # Simulate loading time (5 seconds)
    QTimer.singleShot(5000, app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
