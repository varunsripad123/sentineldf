#!/usr/bin/env python3
"""Generate metrics report from recent scan logs.

This script reads the latest scan reports from reports/scan_*.json
and computes aggregate statistics for monitoring.

Usage:
    python scripts/metrics_report.py [--days N] [--output FILE]
    make metrics
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


def load_scan_reports(reports_dir: Path, days: int = 7) -> List[Dict[str, Any]]:
    """Load scan reports from the last N days.
    
    Args:
        reports_dir: Directory containing scan_*.json files.
        days: Number of days to look back.
    
    Returns:
        List of scan report dictionaries.
    """
    cutoff = datetime.now() - timedelta(days=days)
    reports = []
    
    if not reports_dir.exists():
        return reports
    
    for scan_file in sorted(reports_dir.glob("scan_*.json")):
        try:
            # Parse timestamp from filename: scan_20241016_123456.json
            timestamp_str = scan_file.stem.split("_")[1] + scan_file.stem.split("_")[2]
            scan_time = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            
            if scan_time >= cutoff:
                with open(scan_file) as f:
                    report = json.load(f)
                    report["_file"] = scan_file.name
                    report["_timestamp"] = scan_time.isoformat()
                    reports.append(report)
        except (ValueError, IndexError, KeyError, json.JSONDecodeError) as e:
            print(f"⚠️  Skipping {scan_file.name}: {e}", file=sys.stderr)
            continue
    
    return reports


def compute_metrics(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate metrics from scan reports.
    
    Args:
        reports: List of scan report dictionaries.
    
    Returns:
        Dictionary with computed metrics.
    """
    if not reports:
        return {
            "total_scans": 0,
            "total_documents": 0,
            "total_quarantined": 0,
            "total_allowed": 0,
            "avg_risk": 0.0,
            "max_risk": 0,
            "min_risk": 0,
            "p50_risk": 0.0,
            "p95_risk": 0.0,
            "quarantine_rate": 0.0,
        }
    
    # Aggregate stats
    total_scans = len(reports)
    total_documents = sum(r.get("summary", {}).get("total_docs", 0) for r in reports)
    total_quarantined = sum(r.get("summary", {}).get("quarantined_count", 0) for r in reports)
    total_allowed = sum(r.get("summary", {}).get("allowed_count", 0) for r in reports)
    
    # Collect all risk scores
    all_risks = []
    for report in reports:
        results = report.get("results", [])
        for result in results:
            risk = result.get("risk", 0)
            all_risks.append(risk)
    
    if not all_risks:
        return {
            "total_scans": total_scans,
            "total_documents": total_documents,
            "total_quarantined": total_quarantined,
            "total_allowed": total_allowed,
            "avg_risk": 0.0,
            "max_risk": 0,
            "min_risk": 0,
            "p50_risk": 0.0,
            "p95_risk": 0.0,
            "quarantine_rate": 0.0,
        }
    
    all_risks.sort()
    
    avg_risk = sum(all_risks) / len(all_risks)
    max_risk = max(all_risks)
    min_risk = min(all_risks)
    p50_risk = all_risks[len(all_risks) // 2]
    p95_risk = all_risks[int(len(all_risks) * 0.95)]
    quarantine_rate = (total_quarantined / total_documents * 100) if total_documents > 0 else 0.0
    
    return {
        "total_scans": total_scans,
        "total_documents": total_documents,
        "total_quarantined": total_quarantined,
        "total_allowed": total_allowed,
        "avg_risk": round(avg_risk, 2),
        "max_risk": max_risk,
        "min_risk": min_risk,
        "p50_risk": round(p50_risk, 2),
        "p95_risk": round(p95_risk, 2),
        "quarantine_rate": round(quarantine_rate, 2),
    }


def print_ascii_report(metrics: Dict[str, Any], days: int) -> None:
    """Print a neat ASCII metrics report.
    
    Args:
        metrics: Computed metrics dictionary.
        days: Number of days covered in report.
    """
    print()
    print("=" * 60)
    print(f"📊 SentinelDF Metrics Report (Last {days} Days)".center(60))
    print("=" * 60)
    print()
    
    if metrics["total_scans"] == 0:
        print("⚠️  No scan reports found in the specified period.")
        print()
        return
    
    # Scan Summary
    print("📈 Scan Summary")
    print("-" * 60)
    print(f"   Total Scans:        {metrics['total_scans']:,}")
    print(f"   Total Documents:    {metrics['total_documents']:,}")
    print(f"   Quarantined:        {metrics['total_quarantined']:,} ({metrics['quarantine_rate']:.1f}%)")
    print(f"   Allowed:            {metrics['total_allowed']:,} ({100 - metrics['quarantine_rate']:.1f}%)")
    print()
    
    # Risk Distribution
    print("⚠️  Risk Distribution")
    print("-" * 60)
    print(f"   Average Risk:       {metrics['avg_risk']:.2f}")
    print(f"   Median (P50):       {metrics['p50_risk']:.2f}")
    print(f"   95th Percentile:    {metrics['p95_risk']:.2f}")
    print(f"   Max Risk:           {metrics['max_risk']}")
    print(f"   Min Risk:           {metrics['min_risk']}")
    print()
    
    # Health Check
    print("✅ Health Check")
    print("-" * 60)
    
    # Check against target KPIs (from PRODUCT_METRICS.md)
    warnings = []
    
    if metrics['quarantine_rate'] < 10:
        print("   ✅ Quarantine rate: GOOD (<10% FP likely)")
    elif metrics['quarantine_rate'] < 20:
        print("   ⚠️  Quarantine rate: WARNING (10-20% FP possible)")
        warnings.append("High quarantine rate - check for false positives")
    else:
        print("   🚨 Quarantine rate: CRITICAL (>20% FP likely)")
        warnings.append("Very high quarantine rate - investigate immediately")
    
    if metrics['avg_risk'] < 30:
        print("   ✅ Average risk: LOW (mostly clean data)")
    elif metrics['avg_risk'] < 50:
        print("   ⚠️  Average risk: MEDIUM (some risky samples)")
    else:
        print("   🚨 Average risk: HIGH (many risky samples)")
        warnings.append("High average risk - verify data quality")
    
    print()
    
    # Warnings
    if warnings:
        print("⚠️  Action Items")
        print("-" * 60)
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
        print()
    
    print("=" * 60)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def save_json_report(metrics: Dict[str, Any], output_file: Path) -> None:
    """Save metrics report as JSON.
    
    Args:
        metrics: Computed metrics dictionary.
        output_file: Path to output JSON file.
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "metrics": metrics,
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ JSON report saved to: {output_file}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate metrics report from scan logs"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save JSON report to file (optional)"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory containing scan reports (default: reports/)"
    )
    
    args = parser.parse_args()
    
    # Load reports
    reports = load_scan_reports(args.reports_dir, args.days)
    
    # Compute metrics
    metrics = compute_metrics(reports)
    
    # Print ASCII report
    print_ascii_report(metrics, args.days)
    
    # Save JSON if requested
    if args.output:
        save_json_report(metrics, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
