# backend/detectors/embedding_outlier.py

"""Embedding-based outlier detector using sentence transformers.

This detector encodes text with a sentence-transformers model and then scores
outliers with IsolationForest. Import of sentence-transformers is fully lazy to
avoid heavyweight deps (torch) at import-time, especially on Windows.

Key points:
- The module-level name `SentenceTransformer` is initialized to None so tests
  can patch it without importing the real library.
- `_lazy_import_st()` prefers the patched module-level name first, and only
  imports the real package as a last resort.
- We never pass the `convert_to_numpy` kwarg (mocks may not accept it).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import numpy as np
from sklearn.ensemble import IsolationForest

# Tests patch this symbol: @patch("backend.detectors.embedding_outlier.SentenceTransformer")
SentenceTransformer = None  # type: ignore


@dataclass
class _MinMax:
    lo: float
    hi: float


class EmbeddingOutlierDetector:
    """Embedding-based outlier detector with IsolationForest.

    Args:
        model_name: sentence-transformers model name.
        contamination: expected outlier fraction for IsolationForest.
        seed: RNG seed.
        encoder: optional injectable encoder(texts)->np.ndarray for tests.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        contamination: float = 0.02,
        seed: int = 7,
        encoder: Optional[Callable[[List[str]], np.ndarray]] = None,
    ) -> None:
        self.model_name = model_name
        self.contamination = float(contamination)
        self.seed = int(seed)

        self._encoder = encoder
        self._st_class = None            # resolved SentenceTransformer class
        self._model = None               # sentence-transformers model instance
        self._iforest: Optional[IsolationForest] = None
        self._scale: Optional[_MinMax] = None
        self._is_fitted = False

    # ---------------- public API ----------------

    def fit(self, corpus_texts: List[str]) -> None:
        if not corpus_texts:
            raise ValueError("corpus_texts cannot be empty")

        X = self._encode(corpus_texts)

        self._iforest = IsolationForest(
            n_estimators=200,
            contamination=self.contamination,
            random_state=self.seed,
        ).fit(X)

        raw = -self._iforest.decision_function(X)  # higher = riskier
        self._scale = _MinMax(lo=float(raw.min()), hi=float(raw.max()))
        self._is_fitted = True

    def score(self, texts: List[str]) -> List[float]:
        if not self._is_fitted or self._iforest is None:
            raise RuntimeError("Detector must be fitted before scoring. Call fit() first.")
        if not texts:
            raise ValueError("texts cannot be empty")

        X = self._encode(texts)
        raw = -self._iforest.decision_function(X)

        lo = self._scale.lo if self._scale else float(raw.min())
        hi = self._scale.hi if self._scale else float(raw.max())
        denom = max(hi - lo, 1e-9)
        norm = np.clip((raw - lo) / denom, 0.0, 1.0)
        return [float(v) for v in norm.tolist()]

    # ---------------- internals ----------------

    def _encode(self, texts: List[str]) -> np.ndarray:
        # Prefer injected encoder for tests (avoids model + torch entirely)
        if self._encoder is not None:
            return self._ensure_2d(self._encoder(texts))

        # Lazy resolve class + model
        self._lazy_import_st()
        if self._model is None:
            self._model = self._st_class(self.model_name)  # type: ignore[operator]

        # Do NOT pass convert_to_numpy (mocks may not accept it)
        emb = self._model.encode(texts, show_progress_bar=False)  # type: ignore[call-arg]
        return self._ensure_2d(emb)

    def _lazy_import_st(self) -> None:
        """Resolve SentenceTransformer class without eagerly importing torch.

        Order:
        1) If we've already cached a class, keep it.
        2) If the module-level `SentenceTransformer` has been patched by tests,
           use that and skip importing the real package.
        3) Otherwise import the real package as a last resort.
        """
        if self._st_class is not None:
            return

        global SentenceTransformer
        if SentenceTransformer is not None:
            self._st_class = SentenceTransformer  # type: ignore[assignment]
            return

        try:
            from sentence_transformers import SentenceTransformer as ST  # type: ignore
            SentenceTransformer = ST  # cache on the module
            self._st_class = ST
        except Exception as exc:
            raise RuntimeError(
                "sentence-transformers is unavailable; either install it or inject an encoder= in EmbeddingOutlierDetector."
            ) from exc

    @staticmethod
    def _ensure_2d(arr: Any) -> np.ndarray:
        """Convert typical encode() outputs (list, list[list], np.ndarray) to a 2D float32 array."""
        X = np.asarray(arr)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        return X.astype(np.float32, copy=False)
