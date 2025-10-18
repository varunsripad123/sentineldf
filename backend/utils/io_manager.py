"""I/O utilities for loading and saving datasets and results.

This module provides consistent interfaces for reading and writing
data in various formats (CSV, JSON, JSONL, Parquet).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .errors import DataFormatError
from .logging import get_logger

logger = get_logger(__name__)


def read_folder(path: str) -> List[Dict[str, Any]]:
    """Load texts from a folder containing .txt and .jsonl files.

    Normalizes all files to dictionaries with consistent keys:
    - id: Unique identifier (filename without extension)
    - content: Text content
    - metadata: Dictionary with filename, relpath, size

    Args:
        path: Path to the folder to read.

    Returns:
        List of dictionaries with normalized structure.

    Raises:
        FileNotFoundError: If the folder does not exist.
        DataFormatError: If files cannot be read or parsed.

    Example:
        >>> records = read_folder("data/samples")
        >>> print(records[0].keys())
        dict_keys(['id', 'content', 'metadata'])
    """
    folder_path = Path(path)

    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {path}")

    if not folder_path.is_dir():
        raise DataFormatError(f"Path is not a directory: {path}")

    results: List[Dict[str, Any]] = []

    # Get all .txt and .jsonl files
    txt_files = list(folder_path.glob("**/*.txt"))
    jsonl_files = list(folder_path.glob("**/*.jsonl"))

    all_files = txt_files + jsonl_files

    if not all_files:
        logger.warning(f"No .txt or .jsonl files found in {path}")
        return results

    for file_path in all_files:
        try:
            # Skip zero-length files
            if file_path.stat().st_size == 0:
                logger.warning(f"Skipping zero-length file: {file_path}")
                continue

            # Read file based on extension
            if file_path.suffix == ".txt":
                record = _read_txt_file(file_path, folder_path)
            elif file_path.suffix == ".jsonl":
                records_from_jsonl = _read_jsonl_file(file_path, folder_path)
                results.extend(records_from_jsonl)
                continue
            else:
                continue

            results.append(record)

        except UnicodeDecodeError as e:
            logger.warning(
                f"Encoding error reading {file_path}, skipping: {e}"
            )
            continue
        except Exception as e:
            raise DataFormatError(
                f"Failed to read file {file_path}: {e}"
            ) from e

    return results


def _read_txt_file(file_path: Path, base_path: Path) -> Dict[str, Any]:
    """Read a single .txt file and normalize to dictionary format.

    Args:
        file_path: Path to the .txt file.
        base_path: Base folder path for computing relative path.

    Returns:
        Normalized dictionary with id, content, and metadata.

    Raises:
        DataFormatError: If the file cannot be read.
    """
    try:
        # Try UTF-8 first, fall back to latin-1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        # Compute relative path
        try:
            relpath = file_path.relative_to(base_path)
        except ValueError:
            relpath = file_path

        record = {
            "id": file_path.stem,
            "content": content,
            "metadata": {
                "filename": file_path.name,
                "relpath": str(relpath),
                "size": file_path.stat().st_size,
            },
        }

        return record

    except Exception as e:
        raise DataFormatError(f"Failed to read {file_path}: {e}") from e


def _read_jsonl_file(
    file_path: Path, base_path: Path
) -> List[Dict[str, Any]]:
    """Read a .jsonl file and normalize to dictionary format.

    Args:
        file_path: Path to the .jsonl file.
        base_path: Base folder path for computing relative path.

    Returns:
        List of normalized dictionaries.

    Raises:
        DataFormatError: If the file cannot be read or parsed.
    """
    results: List[Dict[str, Any]] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Normalize to expected format
                    if isinstance(data, dict):
                        # Extract content field or use entire dict as content
                        content = data.get("content", data.get("text", str(data)))

                        # Generate ID if not present
                        record_id = data.get(
                            "id", f"{file_path.stem}_line_{line_num}"
                        )

                        # Compute relative path
                        try:
                            relpath = file_path.relative_to(base_path)
                        except ValueError:
                            relpath = file_path

                        record = {
                            "id": record_id,
                            "content": content,
                            "metadata": {
                                "filename": file_path.name,
                                "relpath": str(relpath),
                                "size": file_path.stat().st_size,
                                "line_num": line_num,
                            },
                        }

                        results.append(record)

                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Invalid JSON at {file_path}:{line_num}, skipping: {e}"
                    )
                    continue

        return results

    except Exception as e:
        raise DataFormatError(f"Failed to read {file_path}: {e}") from e
