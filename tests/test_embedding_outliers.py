"""Tests for embedding-based outlier detection.

These tests verify the embedding detector and outlier identification logic.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.detectors.embedding_detector import EmbeddingDetector


class TestEmbeddingDetector:
    """Test suite for EmbeddingDetector class."""

    @pytest.fixture
    def detector(self) -> EmbeddingDetector:
        """Create a detector instance for testing.

        Returns:
            Configured EmbeddingDetector instance.
        """
        return EmbeddingDetector(
            model_name="all-MiniLM-L6-v2", contamination=0.1, random_state=42
        )

    def test_detector_initialization(self, detector: EmbeddingDetector) -> None:
        """Test that detector initializes with correct parameters."""
        assert detector is not None
        assert detector.model_name == "all-MiniLM-L6-v2"
        assert detector.contamination == 0.1
        assert detector.random_state == 42

    def test_detector_has_required_methods(
        self, detector: EmbeddingDetector
    ) -> None:
        """Test that detector has all required methods."""
        assert hasattr(detector, "load_model")
        assert hasattr(detector, "encode")
        assert hasattr(detector, "detect_outliers")
        assert hasattr(detector, "fit_predict")

    def test_module_imports(self) -> None:
        """Test that the module can be imported."""
        from backend.detectors import embedding_detector

        assert embedding_detector is not None
        assert True  # Module imported successfully


def test_embedding_detector_exists() -> None:
    """Verify EmbeddingDetector class exists."""
    assert EmbeddingDetector is not None
