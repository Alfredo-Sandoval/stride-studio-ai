#!/usr/bin/env python3
"""
Utility script that creates the stride-studio splash-screen pixmap and saves
the resulting image to simple_splash_save/recordings/splash_image.png.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

# When the script is executed directly from arbitrary locations, make sure the
# repository root (one level above this file) is on sys.path so that the
# `stride_studio` package can be imported without installing it.
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from stride_studio.gui.splash_screen import create_splash_pixmap


def main() -> None:
    """Generate and save the splash-screen image."""
    # Create the recordings directory next to this script
    recordings_dir = REPO_ROOT / "recordings"
    recordings_dir.mkdir(exist_ok=True)

    output_path = recordings_dir / "splash_image.png"

    # Build the splash pixmap and save it
    app = QApplication(sys.argv)
    pixmap = create_splash_pixmap()

    print(f"Saving splash image to: {output_path}")
    success = pixmap.save(str(output_path), "PNG")
    print(f"Image saved: {success}")
    print(f"File exists: {output_path.exists()}")
    print(f"File path: {output_path}")


if __name__ == "__main__":
    sys.exit(main())
