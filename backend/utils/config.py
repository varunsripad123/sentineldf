"""Configuration management for SentinelDF.

This module handles loading and validating configuration from
environment variables and config files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .errors import ConfigError


@dataclass
class AppConfig:
    """Global application configuration.

    Attributes:
        data_dir: Directory for data storage.
        hmac_secret: Secret key for HMAC operations.
        heuristic_weight: Weight for heuristic detector (0.0-1.0).
        embedding_weight: Weight for embedding detector (0.0-1.0).
        risk_quarantine_threshold: Risk score threshold for quarantine (0-100).
    
    Note:
        These defaults can be overridden at runtime via environment variables:
        - HEURISTIC_WEIGHT: Adjust heuristic detector weight
        - EMBEDDING_WEIGHT: Adjust embedding detector weight
        - RISK_QUARANTINE_THRESHOLD: Adjust quarantine threshold
        
        For improved poison detection, consider:
        - heuristic_weight=0.55, embedding_weight=0.45 (bias toward heuristics)
        - risk_quarantine_threshold=60 (lower bar for MVP/testing)
    """

    data_dir: str
    hmac_secret: str
    # Restored test defaults
    heuristic_weight: float = 0.4
    embedding_weight: float = 0.6
    risk_quarantine_threshold: int = 70

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ConfigError: If configuration values are invalid.
        """
        self._validate()

    def _validate(self) -> None:
        """Validate configuration values.

        Raises:
            ConfigError: If any configuration value is invalid.
        """
        if not self.data_dir:
            raise ConfigError("data_dir cannot be empty")

        if not self.hmac_secret:
            raise ConfigError("hmac_secret cannot be empty")

        if not 0.0 <= self.heuristic_weight <= 1.0:
            raise ConfigError(
                f"heuristic_weight must be between 0.0 and 1.0, got {self.heuristic_weight}"
            )

        if not 0.0 <= self.embedding_weight <= 1.0:
            raise ConfigError(
                f"embedding_weight must be between 0.0 and 1.0, got {self.embedding_weight}"
            )

        if not 0 <= self.risk_quarantine_threshold <= 100:
            raise ConfigError(
                f"risk_quarantine_threshold must be between 0 and 100, got {self.risk_quarantine_threshold}"
            )


def get_config() -> AppConfig:
    """Load configuration from environment variables.

    Reads configuration from .env file via python-dotenv, applies defaults,
    and validates types.

    Returns:
        Validated AppConfig instance.

    Raises:
        ConfigError: If required configuration is missing or invalid.

    Example:
        >>> config = get_config()
        >>> print(config.data_dir)
        ./data
    """
    # Load environment variables from .env file
    load_dotenv()

    # Read required fields
    data_dir = os.getenv("DATA_DIR", "./data")
    hmac_secret = os.getenv("HMAC_SECRET", "dev-secret-key-change-in-production")

    # Read optional fields with defaults
    # Restored test defaults - can be overridden via environment variables
    heuristic_weight_str = os.getenv("HEURISTIC_WEIGHT", "0.4")
    embedding_weight_str = os.getenv("EMBEDDING_WEIGHT", "0.6")
    risk_threshold_str = os.getenv("RISK_QUARANTINE_THRESHOLD", "70")

    # Parse and validate types
    try:
        heuristic_weight = float(heuristic_weight_str)
    except ValueError as e:
        raise ConfigError(
            f"Invalid HEURISTIC_WEIGHT: {heuristic_weight_str} (must be float)"
        ) from e

    try:
        embedding_weight = float(embedding_weight_str)
    except ValueError as e:
        raise ConfigError(
            f"Invalid EMBEDDING_WEIGHT: {embedding_weight_str} (must be float)"
        ) from e

    try:
        risk_quarantine_threshold = int(risk_threshold_str)
    except ValueError as e:
        raise ConfigError(
            f"Invalid RISK_QUARANTINE_THRESHOLD: {risk_threshold_str} (must be int)"
        ) from e

    # Create and validate config
    config = AppConfig(
        data_dir=data_dir,
        hmac_secret=hmac_secret,
        heuristic_weight=heuristic_weight,
        embedding_weight=embedding_weight,
        risk_quarantine_threshold=risk_quarantine_threshold,
    )

    return config
