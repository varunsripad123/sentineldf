"""Tests for I/O manager module.

These tests verify file reading and data normalization.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.utils.io_manager import read_folder
from backend.utils.errors import DataFormatError


class TestReadFolder:
    """Test suite for read_folder function."""

    def test_read_folder_with_txt_files(self) -> None:
        """Test reading a folder with .txt files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "file1.txt").write_text("Content of file 1", encoding="utf-8")
            (tmppath / "file2.txt").write_text("Content of file 2", encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 2

            # Check structure
            for record in results:
                assert "id" in record
                assert "content" in record
                assert "metadata" in record
                assert "filename" in record["metadata"]
                assert "relpath" in record["metadata"]
                assert "size" in record["metadata"]

            # Check content
            ids = {r["id"] for r in results}
            assert ids == {"file1", "file2"}

            contents = {r["content"] for r in results}
            assert "Content of file 1" in contents
            assert "Content of file 2" in contents

    def test_read_folder_with_jsonl_files(self) -> None:
        """Test reading a folder with .jsonl files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create JSONL file
            jsonl_content = '{"id": "rec1", "content": "First record"}\n{"id": "rec2", "content": "Second record"}\n'
            (tmppath / "data.jsonl").write_text(jsonl_content, encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 2

            # Check IDs
            ids = [r["id"] for r in results]
            assert "rec1" in ids
            assert "rec2" in ids

            # Check contents
            contents = [r["content"] for r in results]
            assert "First record" in contents
            assert "Second record" in contents

    def test_read_folder_mixed_files(self) -> None:
        """Test reading a folder with mixed .txt and .jsonl files."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create mixed files
            (tmppath / "text1.txt").write_text("Text content", encoding="utf-8")
            (tmppath / "data.jsonl").write_text(
                '{"content": "JSON content"}\n', encoding="utf-8"
            )

            results = read_folder(str(tmppath))

            assert len(results) == 2

            contents = [r["content"] for r in results]
            assert "Text content" in contents
            assert "JSON content" in contents

    def test_read_folder_nonexistent(self) -> None:
        """Test reading a nonexistent folder raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Folder not found"):
            read_folder("/nonexistent/path")

    def test_read_folder_not_a_directory(self) -> None:
        """Test reading a file instead of directory raises DataFormatError."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            file_path = tmppath / "file.txt"
            file_path.write_text("content", encoding="utf-8")

            with pytest.raises(DataFormatError, match="not a directory"):
                read_folder(str(file_path))

    def test_read_folder_empty_directory(self) -> None:
        """Test reading an empty directory returns empty list."""
        with TemporaryDirectory() as tmpdir:
            results = read_folder(str(tmpdir))
            assert results == []

    def test_read_folder_skips_zero_length_files(self) -> None:
        """Test that zero-length files are skipped with warning."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create files
            (tmppath / "empty.txt").write_text("", encoding="utf-8")
            (tmppath / "nonempty.txt").write_text("Content", encoding="utf-8")

            results = read_folder(str(tmppath))

            # Should only have the non-empty file
            assert len(results) == 1
            assert results[0]["content"] == "Content"

    def test_read_folder_nested_directories(self) -> None:
        """Test reading nested directories."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create nested structure
            subdir = tmppath / "subdir"
            subdir.mkdir()
            (tmppath / "root.txt").write_text("Root content", encoding="utf-8")
            (subdir / "nested.txt").write_text("Nested content", encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 2

            contents = {r["content"] for r in results}
            assert "Root content" in contents
            assert "Nested content" in contents

    def test_read_folder_jsonl_with_text_field(self) -> None:
        """Test JSONL with 'text' field instead of 'content'."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            jsonl_content = '{"text": "Using text field"}\n'
            (tmppath / "data.jsonl").write_text(jsonl_content, encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 1
            assert results[0]["content"] == "Using text field"

    def test_read_folder_jsonl_missing_content(self) -> None:
        """Test JSONL without content or text field uses string representation."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            jsonl_content = '{"other_field": "value"}\n'
            (tmppath / "data.jsonl").write_text(jsonl_content, encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 1
            # Should contain the dict as string
            assert "other_field" in results[0]["content"]

    def test_read_folder_jsonl_generates_id(self) -> None:
        """Test that JSONL records without IDs get generated IDs."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            jsonl_content = '{"content": "Record 1"}\n{"content": "Record 2"}\n'
            (tmppath / "data.jsonl").write_text(jsonl_content, encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 2

            # Check that IDs were generated
            ids = [r["id"] for r in results]
            assert "data_line_1" in ids
            assert "data_line_2" in ids

    def test_read_folder_metadata_includes_size(self) -> None:
        """Test that metadata includes file size."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            content = "Test content with some length"
            (tmppath / "test.txt").write_text(content, encoding="utf-8")

            results = read_folder(str(tmppath))

            assert len(results) == 1
            assert results[0]["metadata"]["size"] > 0

    def test_read_folder_ignores_other_extensions(self) -> None:
        """Test that files with other extensions are ignored."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "file.txt").write_text("Text content", encoding="utf-8")
            (tmppath / "file.py").write_text("Python code", encoding="utf-8")
            (tmppath / "file.md").write_text("Markdown", encoding="utf-8")

            results = read_folder(str(tmppath))

            # Should only read .txt file
            assert len(results) == 1
            assert results[0]["content"] == "Text content"
