"""Tests for hashing utilities.

These tests verify hash_text function and DedupeIndex class.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.hashing import DedupeIndex, hash_text
from backend.utils.errors import DataFormatError


class TestHashText:
    """Test suite for hash_text function."""

    def test_hash_text_deterministic(self) -> None:
        """Test that hashing the same text produces the same hash."""
        text = "Hello, World!"
        hash1 = hash_text(text)
        hash2 = hash_text(text)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters

    def test_hash_text_different_inputs(self) -> None:
        """Test that different inputs produce different hashes."""
        hash1 = hash_text("Hello, World!")
        hash2 = hash_text("Goodbye, World!")

        assert hash1 != hash2

    def test_hash_text_newline_normalization(self) -> None:
        """Test that newlines are normalized across platforms."""
        text_unix = "Line 1\nLine 2\nLine 3"
        text_windows = "Line 1\r\nLine 2\r\nLine 3"
        text_mac = "Line 1\rLine 2\rLine 3"

        hash_unix = hash_text(text_unix)
        hash_windows = hash_text(text_windows)
        hash_mac = hash_text(text_mac)

        # All should produce the same hash after normalization
        assert hash_unix == hash_windows == hash_mac

    def test_hash_text_empty_string(self) -> None:
        """Test hashing an empty string."""
        hash_empty = hash_text("")

        assert len(hash_empty) == 64
        assert hash_empty == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_hash_text_unicode(self) -> None:
        """Test hashing Unicode text."""
        text = "Hello 世界! 🌍"
        hash_result = hash_text(text)

        assert len(hash_result) == 64
        # Should be deterministic
        assert hash_result == hash_text(text)


class TestDedupeIndex:
    """Test suite for DedupeIndex class."""

    def test_dedupe_index_initialization(self) -> None:
        """Test that DedupeIndex initializes correctly."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "test_index.json"
            index = DedupeIndex(index_path=index_path)

            assert index.index_path == index_path
            assert index.size() == 0

    def test_dedupe_index_add_and_contains(self) -> None:
        """Test adding hashes and checking containment."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "test_index.json"
            index = DedupeIndex(index_path=index_path)

            hash1 = "abc123"
            hash2 = "def456"

            index.add(hash1)
            assert index.contains(hash1)
            assert not index.contains(hash2)

            index.add(hash2)
            assert index.contains(hash1)
            assert index.contains(hash2)
            assert index.size() == 2

    def test_dedupe_index_duplicate_add(self) -> None:
        """Test that adding duplicate hashes doesn't increase size."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "test_index.json"
            index = DedupeIndex(index_path=index_path)

            hash1 = "abc123"

            index.add(hash1)
            assert index.size() == 1

            index.add(hash1)
            assert index.size() == 1  # Still 1, not 2

    def test_dedupe_index_save_and_load(self) -> None:
        """Test saving and loading the index from disk."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "test_index.json"

            # Create index and add hashes
            index1 = DedupeIndex(index_path=index_path)
            index1.add("hash1")
            index1.add("hash2")
            index1.add("hash3")
            index1.save()

            # Load in a new instance
            index2 = DedupeIndex(index_path=index_path)
            index2.load()

            assert index2.size() == 3
            assert index2.contains("hash1")
            assert index2.contains("hash2")
            assert index2.contains("hash3")
            assert not index2.contains("hash4")

    def test_dedupe_index_load_nonexistent_file(self) -> None:
        """Test loading when file doesn't exist creates empty index."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "nonexistent.json"
            index = DedupeIndex(index_path=index_path)
            index.load()

            assert index.size() == 0

    def test_dedupe_index_save_creates_directories(self) -> None:
        """Test that save creates parent directories if needed."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "subdir1" / "subdir2" / "index.json"
            index = DedupeIndex(index_path=index_path)
            index.add("test_hash")
            index.save()

            assert index_path.exists()
            assert index_path.parent.exists()

    def test_dedupe_index_load_corrupted_file(self) -> None:
        """Test loading a corrupted index file raises DataFormatError."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "corrupted.json"

            # Write invalid JSON
            with open(index_path, "w") as f:
                f.write("{ invalid json }")

            index = DedupeIndex(index_path=index_path)

            with pytest.raises(DataFormatError, match="Failed to parse index file"):
                index.load()

    def test_dedupe_index_load_invalid_format(self) -> None:
        """Test loading index with invalid format raises DataFormatError."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "invalid.json"

            # Write valid JSON but wrong structure
            with open(index_path, "w") as f:
                f.write('{"wrong_key": []}')

            index = DedupeIndex(index_path=index_path)

            with pytest.raises(DataFormatError, match="missing 'hashes' key"):
                index.load()

    def test_dedupe_index_size(self) -> None:
        """Test that size() returns correct count."""
        with TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "test_index.json"
            index = DedupeIndex(index_path=index_path)

            assert index.size() == 0

            for i in range(10):
                index.add(f"hash_{i}")

            assert index.size() == 10
