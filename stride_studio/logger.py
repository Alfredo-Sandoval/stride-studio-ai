#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  utils/logger.py – central logging bootstrap for Stride Studio
# ---------------------------------------------------------------------------
"""
Package-wide logger initialisation.

Features
--------
* Rotating **file** handler (`~/.stride_studio/stride_studio.log`, 10 MiB × 5)
* Coloured **console** output on TTYs (falls back to plain text otherwise)
* Dynamic level change via :func:`set_level`
* Automatic capture of uncaught exceptions (main thread)
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Final

__all__ = ["init", "set_level", "get_logger", "LOGGER", "LOG_PATH"]

# --------------------------------------------------------------------------- #
# constants
LOG_DIR: Final[Path] = Path.home() / ".stride_studio"
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH: Final[Path] = LOG_DIR / "stride_studio.log"

# single package-root logger
LOGGER: Final[logging.Logger] = logging.getLogger("stride_studio")

# keep handler refs so we can tweak / remove later
_HANDLERS: list[logging.Handler] = []


# --------------------------------------------------------------------------- #
def _build_console_handler(fmt: str, date: str) -> logging.Handler:
    """Return a stream handler with colour if stdout is a TTY."""
    hdl = logging.StreamHandler(sys.stdout)
    hdl.setFormatter(logging.Formatter(fmt, datefmt=date))
    return hdl


def _build_file_handler(fmt: str, date: str) -> logging.Handler:
    hdl = RotatingFileHandler(
        LOG_PATH, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    hdl.setFormatter(logging.Formatter(fmt, datefmt=date))
    return hdl


# --------------------------------------------------------------------------- #
def init(level: int = logging.INFO) -> logging.Logger:
    """
    Configure handlers **once** and return the package logger.

    Re-invocations simply update the level; they do *not* duplicate handlers.
    """
    global _HANDLERS

    fmt = "%(asctime)s  %(levelname)-8s  %(name)s: %(message)s"
    date = "%Y-%m-%d %H:%M:%S"

    if not _HANDLERS:  # first time → create handlers
        file_hdl = _build_file_handler(fmt, date)
        console_hdl = _build_console_handler(fmt, date)
        _HANDLERS.extend([file_hdl, console_hdl])
        for h in _HANDLERS:
            LOGGER.addHandler(h)

        # intercept uncaught exceptions
        def _ex_hook(exctype, value, tb):
            LOGGER.critical("UNCAUGHT EXCEPTION", exc_info=(exctype, value, tb))
            sys.__excepthook__(exctype, value, tb)

        sys.excepthook = _ex_hook

    # set / update level
    LOGGER.setLevel(level)
    for h in _HANDLERS:
        h.setLevel(level)

    LOGGER.info(
        "Logger initialised at %s – log file: %s",
        logging.getLevelName(level),
        LOG_PATH,
    )
    return LOGGER


# --------------------------------------------------------------------------- #
def set_level(level: int) -> None:
    """Change log level for package and all handlers at runtime."""
    if not _HANDLERS:
        LOGGER.warning("Logger not initialised; calling init() implicitly.")
        init(level)
        return

    LOGGER.setLevel(level)
    for h in _HANDLERS:
        h.setLevel(level)
    LOGGER.info("Log level changed to %s", logging.getLevelName(level))


# --------------------------------------------------------------------------- #
def get_logger(name: str | None = None) -> logging.Logger:
    """
    Convenience helper for sub-modules:

    ```python
    log = get_logger(__name__)
    ```
    """
    return logging.getLogger(name or "stride_studio")
