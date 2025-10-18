"""Tests for MBOM (Material Bill of Materials) system.

These tests verify the MBOM signer and ledger functionality.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.mbom.signer import MBOMSigner
from backend.mbom.ledger import MBOMLedger


class TestMBOMSigner:
    """Test suite for MBOMSigner class."""

    @pytest.fixture
    def signer(self) -> MBOMSigner:
        """Create a signer instance for testing.

        Returns:
            Configured MBOMSigner instance.
        """
        return MBOMSigner()

    def test_signer_initialization(self, signer: MBOMSigner) -> None:
        """Test that signer initializes correctly."""
        assert signer is not None
        assert signer.key_path is None

    def test_signer_has_required_methods(self, signer: MBOMSigner) -> None:
        """Test that signer has all required methods."""
        assert hasattr(signer, "generate_keypair")
        assert hasattr(signer, "sign_record")
        assert hasattr(signer, "verify_signature")
        assert hasattr(signer, "create_attestation")


class TestMBOMLedger:
    """Test suite for MBOMLedger class."""

    @pytest.fixture
    def ledger(self, tmp_path: Path) -> MBOMLedger:
        """Create a ledger instance for testing.

        Args:
            tmp_path: Pytest temporary directory fixture.

        Returns:
            Configured MBOMLedger instance.
        """
        ledger_file = tmp_path / "test_ledger.json"
        return MBOMLedger(ledger_path=ledger_file)

    def test_ledger_initialization(self, ledger: MBOMLedger) -> None:
        """Test that ledger initializes correctly."""
        assert ledger is not None
        assert ledger.ledger_path is not None

    def test_ledger_has_required_methods(self, ledger: MBOMLedger) -> None:
        """Test that ledger has all required methods."""
        assert hasattr(ledger, "add_entry")
        assert hasattr(ledger, "get_entry")
        assert hasattr(ledger, "query_lineage")
        assert hasattr(ledger, "save")
        assert hasattr(ledger, "load")
        assert hasattr(ledger, "export_report")


def test_mbom_modules_import() -> None:
    """Test that MBOM modules can be imported."""
    from backend.mbom import signer, ledger

    assert signer is not None
    assert ledger is not None
    assert True  # Modules imported successfully
