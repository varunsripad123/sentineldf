"""Smoke test for Streamlit dashboard.

This module provides a lightweight smoke test that verifies the Streamlit
app module can be imported and contains the expected functions without
running the full event loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStreamlitSmoke:
    """Smoke tests for Streamlit application."""

    def test_import_streamlit_app(self) -> None:
        """Test that streamlit_app module can be imported."""
        try:
            from frontend import streamlit_app
            
            assert streamlit_app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    def test_main_function_exists(self) -> None:
        """Test that main function exists and is callable."""
        from frontend import streamlit_app
        
        assert hasattr(streamlit_app, "main")
        assert callable(streamlit_app.main)

    def test_helper_functions_exist(self) -> None:
        """Test that helper functions exist."""
        from frontend import streamlit_app
        
        # Check key functions exist
        functions = [
            "load_text_files",
            "compute_umap_embeddings",
            "render_sidebar",
            "analyze_documents",
            "render_summary_cards",
            "render_results_table",
            "render_charts",
            "generate_mbom_download",
        ]
        
        for func_name in functions:
            assert hasattr(streamlit_app, func_name), f"Missing function: {func_name}"
            assert callable(getattr(streamlit_app, func_name))

    def test_constants_defined(self) -> None:
        """Test that required constants are defined."""
        from frontend import streamlit_app
        
        assert hasattr(streamlit_app, "UMAP_TIME_BUDGET")
        assert hasattr(streamlit_app, "UMAP_MAX_DOCS")
        assert isinstance(streamlit_app.UMAP_TIME_BUDGET, (int, float))
        assert isinstance(streamlit_app.UMAP_MAX_DOCS, int)

    def test_load_text_files_function(self, tmp_path: Path) -> None:
        """Test load_text_files function with sample data."""
        from frontend import streamlit_app
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        # Test loading single file
        files = streamlit_app.load_text_files(test_file)
        assert len(files) == 1
        assert files[0][0] == "test.txt"
        assert files[0][1] == "Test content"
        
        # Test loading directory
        (tmp_path / "test2.txt").write_text("Content 2")
        files = streamlit_app.load_text_files(tmp_path)
        assert len(files) == 2

    def test_generate_mbom_function(self) -> None:
        """Test MBOM generation function."""
        from frontend import streamlit_app
        
        # Sample results
        results = [
            {
                "doc_id": "test1",
                "risk": 30,
                "quarantine": False,
                "reasons": [],
                "signals": {"heuristic": 0.3, "embedding": 0.3},
                "action": "allow",
            },
            {
                "doc_id": "test2",
                "risk": 80,
                "quarantine": True,
                "reasons": ["High risk"],
                "signals": {"heuristic": 0.8, "embedding": 0.8},
                "action": "quarantine",
            },
        ]
        
        # Generate MBOM
        mbom_bytes = streamlit_app.generate_mbom_download(results, "test@example.com")
        
        assert isinstance(mbom_bytes, bytes)
        assert len(mbom_bytes) > 0
        
        # Parse and validate structure
        import json
        mbom_data = json.loads(mbom_bytes)
        
        assert "mbom_id" in mbom_data
        assert "signature" in mbom_data
        assert "approved_by" in mbom_data
        assert mbom_data["approved_by"] == "test@example.com"
        assert "summary" in mbom_data
        assert mbom_data["summary"]["total_docs"] == 2
        assert mbom_data["summary"]["quarantined"] == 1
