"""Cryptographic hashing utilities for data integrity.

This module provides deterministic hashing functions for datasets,
individual records, and MBOM entries.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Set

from .errors import DataFormatError


def hash_text(text: str) -> str:
    """Compute SHA-256 hash of a text string with normalized newlines.

    Args:
        text: Input text to hash.

    Returns:
        Hexadecimal hash string (64 characters).

    Example:
        >>> hash_text("Hello, World!")
        'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
    """
    # Normalize newlines to ensure consistent hashing across platforms
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Compute SHA-256 hash
    hash_obj = hashlib.sha256(normalized_text.encode("utf-8"))
    return hash_obj.hexdigest()


class DedupeIndex:
    """Hash-based deduplication index with persistent storage.

    This class maintains a set of content hashes to detect duplicate
    entries. The index is persisted to disk in JSON format.

    Attributes:
        index_path: Path to the persistent index file.
        _hashes: Set of content hashes.
    """

    def __init__(self, index_path: str | Path = "data/hash_index.json") -> None:
        """Initialize the deduplication index.

        Args:
            index_path: Path to the index file (default: data/hash_index.json).
        """
        self.index_path = Path(index_path)
        self._hashes: Set[str] = set()

    def load(self) -> None:
        """Load the index from disk.

        Creates an empty index if the file does not exist.

        Raises:
            DataFormatError: If the index file is corrupted or invalid.
        """
        if not self.index_path.exists():
            self._hashes = set()
            return

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "hashes" not in data:
                raise DataFormatError(
                    f"Invalid index format in {self.index_path}: missing 'hashes' key"
                )

            if not isinstance(data["hashes"], list):
                raise DataFormatError(
                    f"Invalid index format in {self.index_path}: 'hashes' must be a list"
                )

            self._hashes = set(data["hashes"])

        except json.JSONDecodeError as e:
            raise DataFormatError(
                f"Failed to parse index file {self.index_path}: {e}"
            ) from e
        except Exception as e:
            raise DataFormatError(
                f"Failed to load index from {self.index_path}: {e}"
            ) from e

    def save(self) -> None:
        """Save the index to disk with atomic write.

        Creates parent directories if they don't exist. Uses atomic write
        by writing to a temporary file first, then renaming.

        Raises:
            DataFormatError: If saving fails.
        """
        # Create parent directories if needed
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first for atomic operation
        temp_path = self.index_path.with_suffix(".tmp")

        try:
            data = {"hashes": sorted(list(self._hashes))}

            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_path.replace(self.index_path)

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise DataFormatError(
                f"Failed to save index to {self.index_path}: {e}"
            ) from e

    def add(self, hash_value: str) -> None:
        """Add a hash to the index.

        Args:
            hash_value: Hash string to add.

        Example:
            >>> index = DedupeIndex()
            >>> index.add("abc123")
            >>> index.contains("abc123")
            True
        """
        self._hashes.add(hash_value)

    def contains(self, hash_value: str) -> bool:
        """Check if a hash exists in the index.

        Args:
            hash_value: Hash string to check.

        Returns:
            True if the hash exists, False otherwise.

        Example:
            >>> index = DedupeIndex()
            >>> index.add("abc123")
            >>> index.contains("abc123")
            True
            >>> index.contains("xyz789")
            False
        """
        return hash_value in self._hashes

    def size(self) -> int:
        """Get the number of hashes in the index.

        Returns:
            Number of unique hashes in the index.

        Example:
            >>> index = DedupeIndex()
            >>> index.add("abc123")
            >>> index.add("def456")
            >>> index.size()
            2
        """
        return len(self._hashes)
