"""Custom exception classes for SentinelDF.

This module defines a hierarchy of exception classes for structured
error handling throughout the application.
"""

from __future__ import annotations


class SentinelError(Exception):
    """Base exception class for all SentinelDF errors."""

    pass


class ConfigError(SentinelError):
    """Exception raised for configuration-related errors."""

    pass


class DataFormatError(SentinelError):
    """Exception raised for data format and validation errors."""

    pass


class DetectorError(SentinelError):
    """Exception raised for detector-related errors."""

    pass
