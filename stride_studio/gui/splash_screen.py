#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  gui/splash_screen.py – Stride Studio splash screen
# ---------------------------------------------------------------------------

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont
from PySide6.QtWidgets import QSplashScreen
import os


def create_splash_pixmap(size=QSize(720, 480)):
    """
    Create splash screen pixmap using Splash_Image.png and resize it to a reasonable size
    """
    # Load the splash image from file
    splash_image_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Splash_Image.png"
    )
    original_pixmap = QPixmap(splash_image_path)

    # Downscale the image to a reasonable size
    pixmap = original_pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # Create a painter to draw on the image
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    # Add a loading bar at the bottom of the image
    bar_width = pixmap.width() * 0.8
    bar_height = 8
    bar_x = (pixmap.width() - bar_width) / 2
    bar_y = pixmap.height() * 0.9  # Position closer to bottom

    # Bar background - semi-transparent
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(30, 30, 40, 120))
    painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 4, 4)

    # Bar fill gradient - this will be fully filled initially
    fill_gradient = QLinearGradient(bar_x, 0, bar_x + bar_width, 0)
    fill_gradient.setColorAt(0, QColor(0, 210, 255))
    fill_gradient.setColorAt(1, QColor(120, 80, 255))

    painter.setBrush(fill_gradient)
    painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 4, 4)

    # Add version and author information
    footer_font = QFont("Arial", 10)
    painter.setFont(footer_font)

    # Version on right
    painter.setPen(QColor(255, 255, 255, 180))
    painter.drawText(
        0,
        pixmap.height() - 30,
        pixmap.width(),
        30,
        Qt.AlignRight | Qt.AlignVCenter,
        "v1.0.0  ",
    )

    # Author name in center with copyright symbol
    painter.setPen(QColor(255, 255, 255, 180))
    copyright_text = "\xa9 2025 Alfredo Sandoval"
    painter.drawText(
        0,
        pixmap.height() - 30,
        pixmap.width(),
        30,
        Qt.AlignHCenter | Qt.AlignVCenter,
        copyright_text,
    )

    painter.end()
    return pixmap


class StrideStudioSplash(QSplashScreen):
    """
    Animated splash screen for Stride Studio
    """

    def __init__(self, app=None):
        self.pixmap = create_splash_pixmap()
        super().__init__(self.pixmap)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.app = app

        # Setup animation
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(35)  # update every 35ms

    def _update_progress(self):
        """Animate the progress bar"""
        self.progress += 1
        if self.progress > 100:
            self.timer.stop()
            return

        # Redraw the pixmap with updated progress bar
        size = self.pixmap.size()
        painter = QPainter(self.pixmap)

        # Bar dimensions
        bar_width = size.width() * 0.8
        bar_height = 8
        bar_x = (size.width() - bar_width) / 2
        bar_y = size.height() * 0.9  # Position closer to bottom

        # Clear previous progress
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 40, 120))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 4, 4)

        # Draw updated progress
        fill_gradient = QLinearGradient(bar_x, 0, bar_x + bar_width, 0)
        fill_gradient.setColorAt(0, QColor(0, 210, 255))
        fill_gradient.setColorAt(1, QColor(120, 80, 255))

        painter.setBrush(fill_gradient)
        progress_width = bar_width * (self.progress / 100.0)
        painter.drawRoundedRect(bar_x, bar_y, progress_width, bar_height, 4, 4)

        # If we have an application, process its events to keep UI responsive
        if self.app:
            self.app.processEvents()

        # Update splash screen with new pixmap
        self.setPixmap(self.pixmap)
        painter.end()

    def show_and_finish(self, main_window, duration=2500):
        """Show splash screen and close it after window is loaded"""
        self.show()

        # Start a timer to close the splash after duration
        QTimer.singleShot(duration, lambda: self._finish_splash(main_window))

    def _finish_splash(self, main_window):
        """Finish the splash screen and show the main window"""
        main_window.show()
        self.finish(main_window)


# For testing
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    splash = StrideStudioSplash(app)
    splash.show()

    # Simulate loading time
    QTimer.singleShot(3000, app.quit)

    sys.exit(app.exec())
