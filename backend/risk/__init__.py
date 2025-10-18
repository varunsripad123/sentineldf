"""Risk assessment and fusion modules."""

from .fusion import fuse_scores, reason_from_embed, reason_from_heur

__all__ = ["fuse_scores", "reason_from_heur", "reason_from_embed"]
