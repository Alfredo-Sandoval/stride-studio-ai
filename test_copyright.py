#!/usr/bin/env python3
# Test for copyright symbol

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt
import sys

def main():
    app = QApplication(sys.argv)
    
    # Create a label with copyright symbol
    copyright_text = "\u00a9 2025 Alfredo Sandoval"  # Unicode for copyright symbol
    label = QLabel(copyright_text)
    label.setStyleSheet("font-size: 24px; padding: 20px;")
    label.setAlignment(Qt.AlignCenter)
    label.resize(400, 100)
    label.show()
    
    return app.exec()

if __name__ == "__main__":
    main()
