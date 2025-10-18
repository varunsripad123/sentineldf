"""Logging utilities for SentinelDF.

This module provides consistent logging configuration across the application.
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Name of the logger (typically __name__ of the calling module).

    Returns:
        Configured logger instance with consistent formatting.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger
