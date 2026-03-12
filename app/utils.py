"""
utils.py - Utility functions for Netscope.

Provides logging setup used across the project.
"""

import logging
import os

from app.config import LOG_FILE


def setup_logger() -> logging.Logger:
    """
    Configure and return the application logger.

    Logs are sent to both the console (INFO+) and a file (DEBUG+).
    The log file is created automatically if it doesn't exist.
    """
    # Ensure the log directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Create a named logger for the project
    logger = logging.getLogger("netscope")
    logger.setLevel(logging.DEBUG)

    # Shared formatter: timestamp | level | message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler - shows INFO and above to the user
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler - records DEBUG and above for troubleshooting
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Avoid adding duplicate handlers if setup_logger is called twice
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger