"""Centralized logging configuration for the application.

This module provides a single source of truth for logging setup to avoid
duplicate log messages and ensure consistent formatting across the application.
"""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the application.

    Sets up logging with a consistent format and prevents duplicate handlers
    in test environments. This should be called once at application startup.

    Args:
        level: Log level string (default: "INFO"). Valid values are:
               "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".

    Example:
        >>> configure_logging("DEBUG")
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    # Force handlers to avoid duplicates (important for tests)
    root_logger = logging.getLogger()
    
    # Remove existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure with clean setup
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,  # Python 3.8+ - forces reconfiguration
    )
