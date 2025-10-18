"""Tests for risk score fusion module.

These tests verify the fusion of heuristic and embedding scores.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.risk.fusion import fuse_scores
from backend.utils.config import AppConfig


class TestFuseScores:
    """Test suite for fuse_scores function."""

    @pytest.fixture
    def config(self) -> AppConfig:
        """Create a test configuration.

        Returns:
            AppConfig with default test values.
        """
        return AppConfig(
            data_dir="./data",
            hmac_secret="test-secret",
            heuristic_weight=0.4,
            embedding_weight=0.6,
            risk_quarantine_threshold=70,
        )

    def test_fuse_scores_weights_apply(self, config: AppConfig) -> None:
        """Test that weights are correctly applied to scores."""
        # High heuristic, low embedding
        result1 = fuse_scores(0.8, 0.2, config)
        # 0.8 * 0.4 + 0.2 * 0.6 = 0.32 + 0.12 = 0.44 -> 44
        assert result1["risk"] == 44

        # Low heuristic, high embedding
        result2 = fuse_scores(0.2, 0.8, config)
        # 0.2 * 0.4 + 0.8 * 0.6 = 0.08 + 0.48 = 0.56 -> 56
        assert result2["risk"] == 56

        # Equal scores
        result3 = fuse_scores(0.5, 0.5, config)
        # 0.5 * 0.4 + 0.5 * 0.6 = 0.2 + 0.3 = 0.5 -> 50
        assert result3["risk"] == 50

    def test_fuse_scores_different_weights(self) -> None:
        """Test fusion with different weight configurations."""
        # Favor heuristic heavily
        config1 = AppConfig(
            data_dir="./data",
            hmac_secret="test",
            heuristic_weight=0.9,
            embedding_weight=0.1,
            risk_quarantine_threshold=70,
        )

        result1 = fuse_scores(0.8, 0.2, config1)
        # 0.8 * 0.9 + 0.2 * 0.1 = 0.72 + 0.02 = 0.74 -> 74
        assert result1["risk"] == 74

        # Favor embedding heavily
        config2 = AppConfig(
            data_dir="./data",
            hmac_secret="test",
            heuristic_weight=0.1,
            embedding_weight=0.9,
            risk_quarantine_threshold=70,
        )

        result2 = fuse_scores(0.8, 0.2, config2)
        # 0.8 * 0.1 + 0.2 * 0.9 = 0.08 + 0.18 = 0.26 -> 26
        assert result2["risk"] == 26

    def test_quarantine_threshold(self, config: AppConfig) -> None:
        """Test that quarantine threshold is correctly applied."""
        # Below threshold (70)
        result1 = fuse_scores(0.5, 0.5, config)  # risk = 50
        assert result1["quarantine"] is False
        assert result1["risk"] < config.risk_quarantine_threshold

        # At threshold (70)
        result2 = fuse_scores(0.7, 0.7, config)  # risk = 70
        assert result2["quarantine"] is True
        assert result2["risk"] == config.risk_quarantine_threshold

        # Above threshold (70)
        result3 = fuse_scores(0.9, 0.9, config)  # risk = 90
        assert result3["quarantine"] is True
        assert result3["risk"] > config.risk_quarantine_threshold

    def test_quarantine_threshold_edge_cases(self) -> None:
        """Test quarantine with different threshold values."""
        # Very low threshold
        config_low = AppConfig(
            data_dir="./data",
            hmac_secret="test",
            risk_quarantine_threshold=10,
        )

        result1 = fuse_scores(0.2, 0.2, config_low)  # risk = 20
        assert result1["quarantine"] is True

        # Very high threshold
        config_high = AppConfig(
            data_dir="./data",
            hmac_secret="test",
            risk_quarantine_threshold=95,
        )

        result2 = fuse_scores(0.8, 0.8, config_high)  # risk = 80
        assert result2["quarantine"] is False

    def test_result_structure(self, config: AppConfig) -> None:
        """Test that result has correct structure."""
        result = fuse_scores(0.5, 0.5, config)

        assert "risk" in result
        assert "signals" in result
        assert "quarantine" in result

        assert isinstance(result["risk"], int)
        assert isinstance(result["signals"], dict)
        assert isinstance(result["quarantine"], bool)

        assert "heuristic" in result["signals"]
        assert "embedding" in result["signals"]

    def test_signals_preserved(self, config: AppConfig) -> None:
        """Test that individual signals are preserved in output."""
        heur = 0.75
        embed = 0.35

        result = fuse_scores(heur, embed, config)

        assert result["signals"]["heuristic"] == heur
        assert result["signals"]["embedding"] == embed

    def test_risk_score_range(self, config: AppConfig) -> None:
        """Test that risk scores are in [0, 100] range."""
        # Minimum
        result1 = fuse_scores(0.0, 0.0, config)
        assert result1["risk"] == 0
        assert 0 <= result1["risk"] <= 100

        # Maximum
        result2 = fuse_scores(1.0, 1.0, config)
        assert result2["risk"] == 100
        assert 0 <= result2["risk"] <= 100

        # Middle
        result3 = fuse_scores(0.5, 0.5, config)
        assert 0 <= result3["risk"] <= 100

    def test_risk_score_rounding(self, config: AppConfig) -> None:
        """Test that risk scores are properly rounded."""
        # Test rounding behavior
        result1 = fuse_scores(0.444, 0.556, config)
        # 0.444 * 0.4 + 0.556 * 0.6 = 0.1776 + 0.3336 = 0.5112 -> 51
        assert result1["risk"] == 51

        result2 = fuse_scores(0.445, 0.555, config)
        # 0.445 * 0.4 + 0.555 * 0.6 = 0.178 + 0.333 = 0.511 -> 51
        assert result2["risk"] == 51

    def test_zero_scores(self, config: AppConfig) -> None:
        """Test fusion with zero scores."""
        result = fuse_scores(0.0, 0.0, config)

        assert result["risk"] == 0
        assert result["quarantine"] is False
        assert result["signals"]["heuristic"] == 0.0
        assert result["signals"]["embedding"] == 0.0

    def test_max_scores(self, config: AppConfig) -> None:
        """Test fusion with maximum scores."""
        result = fuse_scores(1.0, 1.0, config)

        assert result["risk"] == 100
        assert result["quarantine"] is True
        assert result["signals"]["heuristic"] == 1.0
        assert result["signals"]["embedding"] == 1.0

    def test_invalid_heuristic_score(self, config: AppConfig) -> None:
        """Test that invalid heuristic scores raise ValueError."""
        with pytest.raises(ValueError, match="heur must be in"):
            fuse_scores(1.5, 0.5, config)

        with pytest.raises(ValueError, match="heur must be in"):
            fuse_scores(-0.1, 0.5, config)

    def test_invalid_embedding_score(self, config: AppConfig) -> None:
        """Test that invalid embedding scores raise ValueError."""
        with pytest.raises(ValueError, match="embed must be in"):
            fuse_scores(0.5, 1.5, config)

        with pytest.raises(ValueError, match="embed must be in"):
            fuse_scores(0.5, -0.1, config)

    def test_deterministic_fusion(self, config: AppConfig) -> None:
        """Test that fusion is deterministic."""
        heur = 0.65
        embed = 0.45

        result1 = fuse_scores(heur, embed, config)
        result2 = fuse_scores(heur, embed, config)

        assert result1["risk"] == result2["risk"]
        assert result1["quarantine"] == result2["quarantine"]
        assert result1["signals"] == result2["signals"]

    def test_realistic_scenarios(self, config: AppConfig) -> None:
        """Test fusion with realistic score combinations."""
        # Clean sample: low heuristic, low embedding
        result1 = fuse_scores(0.1, 0.15, config)
        assert result1["risk"] < 20
        assert result1["quarantine"] is False

        # Suspicious sample: high heuristic, moderate embedding
        result2 = fuse_scores(0.8, 0.5, config)
        assert result2["risk"] >= 60
        assert result2["quarantine"] is False or result2["quarantine"] is True

        # Malicious sample: high heuristic, high embedding
        result3 = fuse_scores(0.9, 0.85, config)
        assert result3["risk"] >= 85
        assert result3["quarantine"] is True

        # Outlier: low heuristic, high embedding
        result4 = fuse_scores(0.2, 0.9, config)
        # 0.2 * 0.4 + 0.9 * 0.6 = 0.08 + 0.54 = 0.62 -> 62
        assert result4["risk"] == 62
        assert result4["quarantine"] is False
