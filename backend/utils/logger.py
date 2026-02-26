"""
Zyga Research & Enrichment Agent — Structured Logging
"""

import logging
import sys

from backend.config import settings


def get_logger(name: str) -> logging.Logger:
    """Create a structured logger for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        level = logging.DEBUG if settings.DEBUG else logging.INFO
        logger.setLevel(level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)-30s │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
