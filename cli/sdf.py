"""SentinelDF command-line interface.

This module provides a CLI for running detections, managing MBOM records,
and validating signed reports from the terminal.
"""

from __future__ import annotations

import glob
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import click

# Import backend functions to reuse logic
try:
    from backend.app import (
        DocumentInput,
        DocumentResult,
        _analyze_document,
        _generate_batch_id,
        _sign_mbom,
    )
    from backend.utils.config import get_config
except ImportError:
    click.echo("Error: Backend modules not available", err=True)
    sys.exit(1)


def _ensure_reports_dir() -> Path:
    """Ensure reports directory exists."""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


def _load_text_files(path: Path) -> List[str]:
    """Load all text files from a directory or single file."""
    texts = []
    if path.is_dir():
        for file_path in sorted(path.glob("*.txt")):
            try:
                texts.append(file_path.read_text(encoding="utf-8"))
            except Exception as e:
                click.echo(f"⚠️  Warning: Could not read {file_path}: {e}", err=True)
    elif path.is_file():
        texts.append(path.read_text(encoding="utf-8"))
    else:
        raise click.BadParameter(f"Path not found: {path}")
    return texts


@click.group()
@click.version_option(version="1.0.0", prog_name="sdf")
def cli():
    """SentinelDF - Data Firewall for LLM Training.
    
    Scan documents for threats, create signed MBOMs, and validate integrity.
    """
    pass


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to data samples directory or file",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Custom output path (default: reports/scan_{timestamp}.json)",
)
def scan(path: Path, output: Path | None) -> None:
    """Scan documents for threats and generate report.
    
    Analyzes all .txt files in the specified directory (or single file)
    and writes a detailed JSON report with risk scores and recommendations.
    
    Example:
        sdf scan --path data/samples
    """
    try:
        # Load configuration
        click.echo("🔧 Loading configuration...", nl=False)
        cfg = get_config()
        click.secho(" ✓", fg="green")

        # Load text files
        click.echo(f"📂 Loading files from {path}...", nl=False)
        texts = _load_text_files(path)
        click.secho(f" ✓ Found {len(texts)} document(s)", fg="green")

        if not texts:
            click.secho("❌ No documents found to scan", err=True, fg="red")
            sys.exit(1)

        # Analyze documents
        click.echo("🔍 Analyzing documents...")
        results = []
        
        with click.progressbar(texts, label="Processing") as bar:
            for idx, text in enumerate(bar):
                doc = DocumentInput(id=f"doc_{idx}", content=text)
                try:
                    result = _analyze_document(doc, cfg)
                    results.append(result.dict())
                except Exception as e:
                    click.echo(f"\n⚠️  Error analyzing document {idx}: {e}", err=True)
                    results.append({
                        "doc_id": f"doc_{idx}",
                        "risk": 0,
                        "quarantine": False,
                        "reasons": [f"Analysis failed: {str(e)}"],
                        "signals": {"heuristic": 0.0, "embedding": 0.0},
                        "action": "allow",
                    })

        # Calculate summary
        quarantined = sum(1 for r in results if r["quarantine"])
        allowed = len(results) - quarantined
        avg_risk = sum(r["risk"] for r in results) / len(results)
        max_risk = max(r["risk"] for r in results)

        summary = {
            "total_docs": len(results),
            "quarantined_count": quarantined,
            "allowed_count": allowed,
            "avg_risk": round(avg_risk, 2),
            "max_risk": max_risk,
            "batch_id": _generate_batch_id(),
        }

        # Prepare report
        report = {
            "scan_metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source_path": str(path),
                "tool_version": "1.0.0",
            },
            "summary": summary,
            "results": results,
        }

        # Write report
        if output is None:
            reports_dir = _ensure_reports_dir()
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output = reports_dir / f"scan_{timestamp}.json"

        output.write_text(json.dumps(report, indent=2))
        click.secho(f"\n✅ Scan complete! Report saved to: {output}", fg="green")

        # Display summary
        click.echo("\n📊 Summary:")
        click.echo(f"   Total documents: {summary['total_docs']}")
        click.secho(f"   Allowed: {summary['allowed_count']}", fg="green")
        if quarantined > 0:
            click.secho(f"   Quarantined: {summary['quarantined_count']}", fg="red")
        else:
            click.echo(f"   Quarantined: {summary['quarantined_count']}")
        click.echo(f"   Average risk: {summary['avg_risk']}")
        click.echo(f"   Max risk: {summary['max_risk']}")
        click.echo(f"   Batch ID: {summary['batch_id']}")

        # Exit with error if any quarantined
        if quarantined > 0:
            click.secho(f"\n⚠️  {quarantined} document(s) flagged for quarantine", fg="yellow")
            sys.exit(1)
        else:
            click.secho("\n✓ All documents passed inspection", fg="green")
            sys.exit(0)

    except Exception as e:
        click.secho(f"❌ Scan failed: {e}", err=True, fg="red")
        sys.exit(1)


@cli.command()
@click.argument(
    "results",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--approver",
    type=str,
    required=True,
    help="Email or identifier of the approver",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Custom output path (default: reports/mbom_{timestamp}.json)",
)
def mbom(results: tuple[Path, ...], approver: str, output: Path | None) -> None:
    """Create signed MBOM from scan results.
    
    Takes scan results and generates a cryptographically signed
    Machine-readable Bill of Materials (MBOM) for audit trails.
    
    Examples:
        sdf mbom reports/scan_*.json --approver you@company.com
        sdf mbom reports/scan_20241016_*.json --approver you@company.com
        sdf mbom reports/scan_latest.json --approver you@company.com
    
    Note: On Windows PowerShell, use single quotes to prevent glob expansion:
        sdf mbom 'reports/scan_*.json' --approver you@company.com
    """
    try:
        # Convert tuple to list of Path objects
        result_files = list(results)
        
        if not result_files:
            click.secho("❌ No result files provided", err=True, fg="red")
            sys.exit(1)

        # Use the most recent file
        result_file = sorted(result_files)[-1]
        
        if len(result_files) > 1:
            click.echo(f"📄 Found {len(result_files)} file(s), using most recent: {result_file}")
        else:
            click.echo(f"📄 Loading scan results from: {result_file}")

        # Load scan results
        scan_data = json.loads(result_file.read_text())
        scan_results = scan_data.get("results", [])
        scan_summary = scan_data.get("summary", {})

        if not scan_results:
            click.secho("❌ No results found in scan file", err=True, fg="red")
            sys.exit(1)

        click.secho(f"✓ Loaded {len(scan_results)} document result(s)", fg="green")

        # Create MBOM
        click.echo("🔐 Generating signed MBOM...", nl=False)
        
        batch_id = scan_summary.get("batch_id", _generate_batch_id())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        mbom_id = f"mbom_{hashlib.md5(f'{batch_id}{timestamp}'.encode()).hexdigest()[:16]}"

        # Calculate summary
        quarantined = sum(1 for r in scan_results if r.get("quarantine", False))
        allowed = len(scan_results) - quarantined
        avg_risk = sum(r.get("risk", 0) for r in scan_results) / len(scan_results)

        summary_data = {
            "total_docs": len(scan_results),
            "quarantined": quarantined,
            "allowed": allowed,
            "avg_risk": round(avg_risk, 2),
        }

        # Create signable payload
        payload = {
            "mbom_id": mbom_id,
            "batch_id": batch_id,
            "approved_by": approver,
            "timestamp": timestamp,
            "summary": summary_data,
            "results_hash": hashlib.sha256(
                json.dumps(scan_results, sort_keys=True).encode()
            ).hexdigest(),
        }

        # Sign
        signature = _sign_mbom(payload)
        click.secho(" ✓", fg="green")

        # Prepare MBOM document
        mbom_doc = {
            "mbom_id": mbom_id,
            "batch_id": batch_id,
            "approved_by": approver,
            "timestamp": timestamp,
            "signature": signature,
            "summary": summary_data,
            "results": scan_results,
            "metadata": {
                "source_file": str(result_file),
                "tool_version": "1.0.0",
            },
        }

        # Write MBOM
        if output is None:
            reports_dir = _ensure_reports_dir()
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            output = reports_dir / f"mbom_{timestamp_str}.json"

        output.write_text(json.dumps(mbom_doc, indent=2))
        click.secho(f"\n✅ MBOM created and signed! Saved to: {output}", fg="green")

        # Display MBOM info
        click.echo("\n📋 MBOM Details:")
        click.echo(f"   MBOM ID: {mbom_id}")
        click.echo(f"   Batch ID: {batch_id}")
        click.echo(f"   Approved by: {approver}")
        click.echo(f"   Timestamp: {timestamp}")
        click.echo(f"   Signature: {signature[:16]}...{signature[-16:]}")
        click.echo(f"   Documents: {summary_data['total_docs']}")
        click.echo(f"   Quarantined: {summary_data['quarantined']}")

        sys.exit(0)

    except Exception as e:
        click.secho(f"❌ MBOM creation failed: {e}", err=True, fg="red")
        sys.exit(1)


@cli.command()
@click.argument(
    "mbom_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, path_type=Path),
)
def validate(mbom_files: tuple[Path, ...]) -> None:
    """Validate signature of MBOM file(s).
    
    Verifies the cryptographic signature and integrity of MBOM documents.
    
    Examples:
        sdf validate reports/mbom_*.json
        sdf validate reports/mbom_20241016_142742.json
        sdf validate reports/mbom_latest.json
    
    Note: On Windows PowerShell, use single quotes to prevent glob expansion:
        sdf validate 'reports/mbom_*.json'
    """
    try:
        # Convert tuple to list
        mbom_list = list(mbom_files)
        
        if not mbom_list:
            click.secho("❌ No MBOM files provided", err=True, fg="red")
            sys.exit(1)

        # Validate all provided files
        all_valid = True
        for mbom_path in sorted(mbom_list):
            click.echo(f"\n🔍 Validating: {mbom_path}")

            # Load MBOM
            mbom_data = json.loads(mbom_path.read_text())

            # Extract signature and payload
            stored_signature = mbom_data.get("signature")
            if not stored_signature:
                click.secho("   ❌ No signature found in MBOM", fg="red")
                all_valid = False
                continue

            # Reconstruct payload
            payload = {
                "mbom_id": mbom_data.get("mbom_id"),
                "batch_id": mbom_data.get("batch_id"),
                "approved_by": mbom_data.get("approved_by"),
                "timestamp": mbom_data.get("timestamp"),
                "summary": mbom_data.get("summary"),
                "results_hash": hashlib.sha256(
                    json.dumps(mbom_data.get("results", []), sort_keys=True).encode()
                ).hexdigest(),
            }

            # Recompute signature
            computed_signature = _sign_mbom(payload)

            # Compare
            if computed_signature == stored_signature:
                click.secho("   ✅ Signature valid", fg="green")
                click.echo(f"      MBOM ID: {mbom_data.get('mbom_id')}")
                click.echo(f"      Approved by: {mbom_data.get('approved_by')}")
                click.echo(f"      Timestamp: {mbom_data.get('timestamp')}")
                click.echo(f"      Documents: {mbom_data.get('summary', {}).get('total_docs', 0)}")
            else:
                click.secho("   ❌ Signature mismatch - MBOM may be tampered!", fg="red")
                click.echo(f"      Expected: {computed_signature[:32]}...")
                click.echo(f"      Got:      {stored_signature[:32]}...")
                all_valid = False

        # Exit code based on validation result
        if all_valid:
            click.secho("\n✅ All MBOMs validated successfully", fg="green")
            sys.exit(0)
        else:
            click.secho("\n❌ Some MBOMs failed validation", fg="red")
            sys.exit(1)

    except Exception as e:
        click.secho(f"❌ Validation failed: {e}", err=True, fg="red")
        sys.exit(1)


def main() -> int:
    """Main entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    sys.exit(main())
