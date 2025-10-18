"""Tests for configuration management module.

These tests verify config loading, validation, and error handling.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.config import AppConfig, get_config
from backend.utils.errors import ConfigError


class TestAppConfig:
    """Test suite for AppConfig dataclass."""

    def test_config_initialization_with_defaults(self) -> None:
        """Test that config initializes with default values."""
        config = AppConfig(data_dir="./data", hmac_secret="test-secret")

        assert config.data_dir == "./data"
        assert config.hmac_secret == "test-secret"
        assert config.heuristic_weight == 0.4
        assert config.embedding_weight == 0.6
        assert config.risk_quarantine_threshold == 70

    def test_config_initialization_with_custom_values(self) -> None:
        """Test that config initializes with custom values."""
        config = AppConfig(
            data_dir="/custom/path",
            hmac_secret="custom-secret",
            heuristic_weight=0.3,
            embedding_weight=0.7,
            risk_quarantine_threshold=80,
        )

        assert config.data_dir == "/custom/path"
        assert config.hmac_secret == "custom-secret"
        assert config.heuristic_weight == 0.3
        assert config.embedding_weight == 0.7
        assert config.risk_quarantine_threshold == 80

    def test_config_validation_empty_data_dir(self) -> None:
        """Test that empty data_dir raises ConfigError."""
        with pytest.raises(ConfigError, match="data_dir cannot be empty"):
            AppConfig(data_dir="", hmac_secret="test-secret")

    def test_config_validation_empty_hmac_secret(self) -> None:
        """Test that empty hmac_secret raises ConfigError."""
        with pytest.raises(ConfigError, match="hmac_secret cannot be empty"):
            AppConfig(data_dir="./data", hmac_secret="")

    def test_config_validation_invalid_heuristic_weight(self) -> None:
        """Test that invalid heuristic_weight raises ConfigError."""
        with pytest.raises(
            ConfigError, match="heuristic_weight must be between 0.0 and 1.0"
        ):
            AppConfig(
                data_dir="./data", hmac_secret="test", heuristic_weight=1.5
            )

    def test_config_validation_negative_heuristic_weight(self) -> None:
        """Test that negative heuristic_weight raises ConfigError."""
        with pytest.raises(
            ConfigError, match="heuristic_weight must be between 0.0 and 1.0"
        ):
            AppConfig(
                data_dir="./data", hmac_secret="test", heuristic_weight=-0.1
            )

    def test_config_validation_invalid_embedding_weight(self) -> None:
        """Test that invalid embedding_weight raises ConfigError."""
        with pytest.raises(
            ConfigError, match="embedding_weight must be between 0.0 and 1.0"
        ):
            AppConfig(
                data_dir="./data", hmac_secret="test", embedding_weight=2.0
            )

    def test_config_validation_invalid_risk_threshold(self) -> None:
        """Test that invalid risk_quarantine_threshold raises ConfigError."""
        with pytest.raises(
            ConfigError, match="risk_quarantine_threshold must be between 0 and 100"
        ):
            AppConfig(
                data_dir="./data", hmac_secret="test", risk_quarantine_threshold=150
            )


class TestGetConfig:
    """Test suite for get_config function."""

    def test_get_config_with_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_config with environment defaults."""
        # Clear relevant environment variables
        monkeypatch.delenv("DATA_DIR", raising=False)
        monkeypatch.delenv("HMAC_SECRET", raising=False)
        monkeypatch.delenv("HEURISTIC_WEIGHT", raising=False)
        monkeypatch.delenv("EMBEDDING_WEIGHT", raising=False)
        monkeypatch.delenv("RISK_QUARANTINE_THRESHOLD", raising=False)

        config = get_config()

        assert config.data_dir == "./data"
        assert config.hmac_secret == "dev-secret-key-change-in-production"
        assert config.heuristic_weight == 0.4
        assert config.embedding_weight == 0.6
        assert config.risk_quarantine_threshold == 70

    def test_get_config_with_environment_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_config with custom environment variables."""
        monkeypatch.setenv("DATA_DIR", "/custom/data")
        monkeypatch.setenv("HMAC_SECRET", "env-secret")
        monkeypatch.setenv("HEURISTIC_WEIGHT", "0.35")
        monkeypatch.setenv("EMBEDDING_WEIGHT", "0.65")
        monkeypatch.setenv("RISK_QUARANTINE_THRESHOLD", "85")

        config = get_config()

        assert config.data_dir == "/custom/data"
        assert config.hmac_secret == "env-secret"
        assert config.heuristic_weight == 0.35
        assert config.embedding_weight == 0.65
        assert config.risk_quarantine_threshold == 85

    def test_get_config_invalid_heuristic_weight_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_config with invalid HEURISTIC_WEIGHT type."""
        monkeypatch.setenv("HEURISTIC_WEIGHT", "not-a-number")

        with pytest.raises(
            ConfigError, match="Invalid HEURISTIC_WEIGHT.*must be float"
        ):
            get_config()

    def test_get_config_invalid_embedding_weight_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_config with invalid EMBEDDING_WEIGHT type."""
        monkeypatch.setenv("EMBEDDING_WEIGHT", "invalid")

        with pytest.raises(
            ConfigError, match="Invalid EMBEDDING_WEIGHT.*must be float"
        ):
            get_config()

    def test_get_config_invalid_risk_threshold_type(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test get_config with invalid RISK_QUARANTINE_THRESHOLD type."""
        monkeypatch.setenv("RISK_QUARANTINE_THRESHOLD", "not-an-int")

        with pytest.raises(
            ConfigError, match="Invalid RISK_QUARANTINE_THRESHOLD.*must be int"
        ):
            get_config()
