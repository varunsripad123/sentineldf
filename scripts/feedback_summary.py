#!/usr/bin/env python3
"""Aggregate user feedback from feedback/*.json files.

This script reads all feedback JSONs and generates a summary report
for review in weekly triage meetings.

Usage:
    python scripts/feedback_summary.py [--days N] [--output FILE]
    make feedback-summary
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List


def load_feedback(feedback_dir: Path, days: int = 7) -> List[Dict[str, Any]]:
    """Load feedback JSONs from the last N days.
    
    Args:
        feedback_dir: Directory containing feedback_*.json files.
        days: Number of days to look back.
    
    Returns:
        List of feedback dictionaries.
    """
    if not feedback_dir.exists():
        feedback_dir.mkdir(parents=True, exist_ok=True)
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    feedbacks = []
    
    for feedback_file in sorted(feedback_dir.glob("feedback_*.json")):
        try:
            with open(feedback_file) as f:
                feedback = json.load(f)
                
                # Parse timestamp from feedback
                timestamp_str = feedback.get("timestamp")
                if timestamp_str:
                    feedback_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    if feedback_time.replace(tzinfo=None) >= cutoff:
                        feedback["_file"] = feedback_file.name
                        feedbacks.append(feedback)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"⚠️  Skipping {feedback_file.name}: {e}", file=sys.stderr)
            continue
    
    return feedbacks


def aggregate_feedback(feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate feedback into summary statistics.
    
    Args:
        feedbacks: List of feedback dictionaries.
    
    Returns:
        Summary dictionary with aggregated stats.
    """
    if not feedbacks:
        return {
            "total_feedback": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "other": 0,
            "by_category": {},
            "top_patterns": [],
        }
    
    # Count by category
    category_counts = Counter()
    pattern_notes = defaultdict(list)
    
    for feedback in feedbacks:
        category = feedback.get("category", "Other")
        category_counts[category] += 1
        
        # Collect notes for pattern analysis
        notes = feedback.get("notes", "").lower()
        if notes:
            pattern_notes[category].append(notes)
    
    # Extract common patterns
    top_patterns = []
    
    # Simple pattern extraction (keywords in notes)
    all_notes = []
    for notes_list in pattern_notes.values():
        all_notes.extend(notes_list)
    
    if all_notes:
        # Count common words (simple heuristic)
        words = []
        for note in all_notes:
            words.extend([w for w in note.split() if len(w) > 3])
        
        word_counts = Counter(words)
        # Top 5 most common words as "patterns"
        for word, count in word_counts.most_common(5):
            if count >= 2:  # Appears at least twice
                top_patterns.append(f"{word} ({count} mentions)")
    
    return {
        "total_feedback": len(feedbacks),
        "false_positives": category_counts.get("False Positive", 0),
        "false_negatives": category_counts.get("False Negative", 0),
        "other": category_counts.get("Other", 0),
        "by_category": dict(category_counts),
        "top_patterns": top_patterns,
    }


def print_ascii_summary(summary: Dict[str, Any], days: int) -> None:
    """Print a neat ASCII feedback summary.
    
    Args:
        summary: Aggregated summary dictionary.
        days: Number of days covered in report.
    """
    print()
    print("=" * 60)
    print(f"📝 Feedback Summary (Last {days} Days)".center(60))
    print("=" * 60)
    print()
    
    if summary["total_feedback"] == 0:
        print("✅ No feedback received in the specified period.")
        print()
        print("This is good news! It means:")
        print("  • Users are satisfied with detection quality")
        print("  • False positive/negative rates are acceptable")
        print("  • Or... users aren't using the feedback feature yet")
        print()
        return
    
    # Overall Stats
    print("📊 Overall Stats")
    print("-" * 60)
    print(f"   Total Feedback:     {summary['total_feedback']:,}")
    print(f"   False Positives:    {summary['false_positives']:,} ({summary['false_positives'] / summary['total_feedback'] * 100:.1f}%)")
    print(f"   False Negatives:    {summary['false_negatives']:,} ({summary['false_negatives'] / summary['total_feedback'] * 100:.1f}%)")
    print(f"   Other Issues:       {summary['other']:,} ({summary['other'] / summary['total_feedback'] * 100:.1f}%)")
    print()
    
    # By Category
    if summary["by_category"]:
        print("📂 Breakdown by Category")
        print("-" * 60)
        for category, count in sorted(summary["by_category"].items(), key=lambda x: x[1], reverse=True):
            pct = count / summary["total_feedback"] * 100
            print(f"   {category:20s} {count:3d} ({pct:5.1f}%)")
        print()
    
    # Top Patterns
    if summary["top_patterns"]:
        print("🔍 Common Patterns")
        print("-" * 60)
        for i, pattern in enumerate(summary["top_patterns"], 1):
            print(f"   {i}. {pattern}")
        print()
    
    # Action Items
    print("✅ Recommended Actions")
    print("-" * 60)
    
    if summary["false_positives"] > 0:
        print(f"   • Review {summary['false_positives']} false positive(s)")
        print("     → Identify common patterns (medical, legal, code)")
        print("     → Consider adding whitelist or tuning threshold")
    
    if summary["false_negatives"] > 0:
        print(f"   • Investigate {summary['false_negatives']} false negative(s)")
        print("     → Add missing patterns to heuristic detector")
        print("     → Check embedding model for drift")
    
    if summary["other"] > 0:
        print(f"   • Triage {summary['other']} other issue(s)")
        print("     → May be bugs, UX issues, or feature requests")
    
    print()
    print("=" * 60)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()


def save_json_summary(summary: Dict[str, Any], output_file: Path, days: int) -> None:
    """Save feedback summary as JSON.
    
    Args:
        summary: Aggregated summary dictionary.
        output_file: Path to output JSON file.
        days: Number of days covered.
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "summary": summary,
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ JSON summary saved to: {output_file}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Aggregate user feedback from feedback/ directory"
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
        help="Save JSON summary to file (optional)"
    )
    parser.add_argument(
        "--feedback-dir",
        type=Path,
        default=Path("feedback"),
        help="Directory containing feedback JSONs (default: feedback/)"
    )
    
    args = parser.parse_args()
    
    # Load feedback
    feedbacks = load_feedback(args.feedback_dir, args.days)
    
    # Aggregate
    summary = aggregate_feedback(feedbacks)
    
    # Print ASCII summary
    print_ascii_summary(summary, args.days)
    
    # Save JSON if requested
    if args.output:
        save_json_summary(summary, args.output, args.days)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
