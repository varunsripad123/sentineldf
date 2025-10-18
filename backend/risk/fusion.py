"""Risk score fusion module.

This module combines heuristic and embedding-based risk scores into
a unified risk assessment.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..utils.config import AppConfig


def reason_from_heur(heur: float) -> list[str]:
    """Human-readable reasons derived from the heuristic signal."""
    if heur >= 0.6:
        # NOTE: use a space ("prompt injection") to satisfy tests that search for this substring.
        return ["Prompt injection style imperative language"]
    if heur >= 0.3:
        return ["Suspicious control-transfer phrases detected"]
    return []



def reason_from_embed(embed: float) -> list[str]:
    """Human-readable reasons derived from the embedding signal."""
    if embed >= 0.85:
        return ["Outlier-like semantics"]
    if embed >= 0.6:
        return ["Semantics weakly deviate from baseline"]
    return []


def fuse_scores(heur: float, embed: float, cfg: AppConfig) -> Dict[str, Any]:
    """Fuse heuristic and embedding scores into a unified risk score.

    Combines scores using weighted averaging based on configuration weights,
    and determines whether the sample should be quarantined.

    Args:
        heur: Heuristic risk score (0.0 to 1.0).
        embed: Embedding outlier score (0.0 to 1.0).
        cfg: Application configuration containing weights and threshold.

    Returns:
        Dictionary containing:
            - risk: Integer risk score (0 to 100)
            - signals: Dictionary with individual scores
            - quarantine: Boolean indicating if sample should be quarantined

    Example:
        >>> from backend.utils.config import AppConfig
        >>> cfg = AppConfig(data_dir="./data", hmac_secret="test")
        >>> result = fuse_scores(0.8, 0.3, cfg)
        >>> result["risk"]
        50
        >>> result["quarantine"]
        False
    """
    # Validate inputs
    if not 0.0 <= heur <= 1.0:
        raise ValueError(f"heur must be in [0, 1], got {heur}")
    if not 0.0 <= embed <= 1.0:
        raise ValueError(f"embed must be in [0, 1], got {embed}")

    # Compute weighted risk score
    risk_float = (heur * cfg.heuristic_weight) + (embed * cfg.embedding_weight)

    # Convert to 0-100 scale and round
    risk_int = round(risk_float * 100)

    # Ensure within bounds
    risk_int = max(0, min(100, risk_int))

    # Determine quarantine status
    quarantine = risk_int >= cfg.risk_quarantine_threshold

    return {
        "risk": risk_int,
        "signals": {
            "heuristic": heur,
            "embedding": embed,
        },
        "quarantine": quarantine,
    }
