#!/usr/bin/env python3
# Test script for the splash screen

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from stride_studio.gui.splash_screen import StrideStudioSplash


def main():
    app = QApplication(sys.argv)
    splash = StrideStudioSplash(app)
    splash.show()

    # Simulate loading time (3 seconds)
    QTimer.singleShot(3000, app.quit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
