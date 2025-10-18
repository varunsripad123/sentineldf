# backend/app.py
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.cache import EmbeddingCache, HeuristicCache
from backend.logging_config import configure_logging
from backend.middleware import RateLimiterMiddleware, RequestContextMiddleware
from backend.risk.fusion import reason_from_embed, reason_from_heur

# --- Logging -----------------------------------------------------------------
# Configure logging at module import
_level = os.getenv("LOG_LEVEL", "INFO").upper()
configure_logging(level=_level)

logger = logging.getLogger("backend.app")

# --- Models ------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of input texts to analyze")


class AnalyzeSignals(BaseModel):
    heuristic: float
    embedding: float


class AnalyzeResult(BaseModel):
    text_id: int
    risk: int  # tests expect int
    quarantine: bool
    reasons: List[str]
    signals: AnalyzeSignals


class AnalyzeResponse(BaseModel):
    results: List[AnalyzeResult]


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    python_version: str
    installed: List[str]


# --- Scan/MBOM Models --------------------------------------------------------
class DocumentInput(BaseModel):
    """Input document for scanning."""
    id: Optional[str] = None
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class ScanRequest(BaseModel):
    """Request to scan documents for threats."""
    docs: List[DocumentInput] = Field(..., min_items=1, max_items=1000)
    dataset: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=1000)


class DocumentResult(BaseModel):
    """Scan result for a single document."""
    doc_id: str
    risk: int
    quarantine: bool
    reasons: List[str]
    signals: AnalyzeSignals
    action: str  # "allow" or "quarantine"


class BatchSummary(BaseModel):
    """Summary statistics for a batch scan."""
    total_docs: int
    quarantined_count: int
    allowed_count: int
    avg_risk: float
    max_risk: int
    batch_id: str


class ScanResponse(BaseModel):
    """Response from document scan."""
    results: List[DocumentResult]
    summary: BatchSummary
    page: int
    page_size: int
    total_pages: int


class MBOMRequest(BaseModel):
    """Request to create signed MBOM."""
    approved_by: str = Field(..., min_length=1)
    results: List[DocumentResult]
    batch_id: Optional[str] = None


class MBOMResponse(BaseModel):
    """Signed MBOM response."""
    mbom_id: str
    batch_id: str
    approved_by: str
    timestamp: str
    results: List[DocumentResult]
    signature: str
    summary: Dict[str, Any]


class ReportResponse(BaseModel):
    """Cached report with results and MBOM."""
    batch_id: str
    results: List[DocumentResult]
    summary: BatchSummary
    mbom: Optional[MBOMResponse] = None
    created_at: str


# --- Heuristic scoring --------------------------------------------------------
_HEURISTIC_PATTERNS: Tuple[Tuple[str, float], ...] = (
    ("ignore previous instructions", 0.75),
    ("ignore all previous instructions", 0.9),
    ("override safety", 0.8),
    ("reveal secrets", 0.7),
    ("disclose secrets", 0.7),
    ("backdoor", 0.7),
    ("do not follow", 0.6),
    ("jailbreak", 0.8),
    ("system prompt", 0.6),
    ("<script>", 0.65),
    ("</script>", 0.65),
    ("onerror=", 0.6),
    ("javascript:", 0.6),
    ("<img", 0.55),
    ("<iframe", 0.55),
)

def _score_heuristic(text: str) -> Tuple[float, List[str]]:
    """Return (score in [0,1], reasons).
    
    Uses the HeuristicDetector class for advanced pattern matching.
    """
    from backend.detectors.heuristic_detector import HeuristicDetector
    
    # Use detector with weight=1.0 to get raw score (not scaled)
    detector = HeuristicDetector(weight=1.0)
    result = detector.detect(text)
    
    return result['score'], result['reasons']


# --- Embedding outlier detector ----------------------------------------------
try:
    from backend.detectors.embedding_outlier import EmbeddingOutlierDetector
except Exception:  # pragma: no cover
    class EmbeddingOutlierDetector:  # type: ignore
        def __init__(self, *_, **__): ...
        def fit(self, __: List[str]) -> None: ...
        def score(self, texts: List[str]) -> List[float]:
            return [0.0 for _ in texts]


# --- App ---------------------------------------------------------------------
app = FastAPI(title="SentinelDF Backend", version="1.0.0")

# Add CORS middleware (allows frontend on localhost:3000 to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# tracing (no-op unless OTEL_EXPORTER_OTLP_ENDPOINT is set)
try:
    from backend.observability.tracing import setup_tracing
    setup_tracing("sentineldf-api")
except Exception:
    pass

# Add middleware
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimiterMiddleware, limit=120, window_sec=60)

_start_time = time.time()

# Module-level caches
HEUR_CACHE = HeuristicCache(maxsize=4096, ttl_sec=900)
EMB_CACHE = EmbeddingCache(maxsize=4096, ttl_sec=900)

_SEED_CORPUS = [
    "Hello there, how can I help you today?",
    "The weather is sunny with a gentle breeze.",
    "This is a normal, harmless message.",
    "We are discussing lunch options for tomorrow.",
    "I enjoy reading books and taking long walks.",
    "Let's schedule a meeting next week to review progress.",
]

_detector: EmbeddingOutlierDetector | None = None


def _initialize_detectors() -> None:
    global _detector
    if _detector is not None:
        return
    _detector = EmbeddingOutlierDetector(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        contamination=0.02,
        seed=7,
    )
    _detector.fit(_SEED_CORPUS)
    logger.info("EmbeddingOutlierDetector initialized.")


# --- Risk fusion --------------------------------------------------------------
def _combine_signals(heuristic: float, embedding: float) -> float:
    """
    Combine signals into a single risk in [0,1].
    Prioritize heuristic so benign < malicious consistently.
    """
    h = max(0.0, min(1.0, heuristic))
    e = max(0.0, min(1.0, embedding))

    if h < 0.15:
        combined = 0.1 * e
    elif h > 0.5:
        combined = min(1.0, 0.8 * h + 0.2 * e)
    else:
        combined = 0.6 * h + 0.4 * e

    return float(max(0.0, min(1.0, combined)))


def _risk_to_int(risk01: float) -> int:
    return int(round(max(0.0, min(1.0, risk01)) * 100))


# --- Routes ------------------------------------------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_texts(req: AnalyzeRequest) -> AnalyzeResponse:
    if not req.texts:
        raise HTTPException(status_code=400, detail="texts cannot be empty")

    # Load configuration
    try:
        from backend.utils.config import get_config
        cfg = get_config()
    except Exception as exc:
        logger.error("Config loading failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load configuration") from exc

    try:
        _initialize_detectors()
    except Exception as exc:
        logger.error("Initialization failed: %s", exc)
        raise HTTPException(status_code=500, detail="") from exc

    assert _detector is not None

    results: List[AnalyzeResult] = []
    
    # Collect texts that need embedding computation
    texts_needing_embed = []
    embed_indices = []
    
    for i, text in enumerate(req.texts):
        # Check heuristic cache
        h_score_cached = HEUR_CACHE.get(text)
        if h_score_cached is None:
            h_score, h_reasons = _score_heuristic(text)
            HEUR_CACHE.set(text, h_score)
        else:
            h_score = h_score_cached
            h_reasons = []  # Reasons not cached, will regenerate
        
        # Check embedding cache
        e_score = EMB_CACHE.get(text)
        if e_score is None:
            texts_needing_embed.append(text)
            embed_indices.append(i)
    
    # Batch compute uncached embeddings
    if texts_needing_embed:
        try:
            e_vals = _detector.score(texts_needing_embed)
            for idx, e_val in zip(embed_indices, e_vals):
                EMB_CACHE.set(req.texts[idx], float(e_val))
        except Exception as exc:
            logger.error("Embedding scoring failed: %s", exc)
            for idx in embed_indices:
                EMB_CACHE.set(req.texts[idx], 0.0)
    
    # Now build results with all cached scores
    for i, text in enumerate(req.texts):
        # Get cached scores
        h_score = HEUR_CACHE.get(text)
        if h_score is None:
            h_score, _ = _score_heuristic(text)
            HEUR_CACHE.set(text, h_score)
        
        e_score = EMB_CACHE.get(text)
        if e_score is None:
            e_score = 0.0
            EMB_CACHE.set(text, e_score)
        
        combined01 = _combine_signals(h_score, e_score)
        risk_int = _risk_to_int(combined01)

        # Build reasons from multiple sources
        reasons: List[str] = []
        
        # Add reason from heuristic score
        reasons += reason_from_heur(h_score)
        
        # Add reason from embedding score
        reasons += reason_from_embed(e_score)
        
        # Add specific pattern match reasons
        _, h_reasons = _score_heuristic(text)
        if h_reasons:
            reasons.extend(h_reasons)
        
        # Check for HTML/JS injection content
        if "<script" in text.lower():
            if "Possible HTML/JS injection content" not in reasons:
                reasons.append("Possible HTML/JS injection content")
        
        # Deduplicate reasons while preserving order
        seen = set()
        deduped_reasons = []
        for reason in reasons:
            if reason not in seen:
                seen.add(reason)
                deduped_reasons.append(reason)
        reasons = deduped_reasons

        # Use configured quarantine threshold
        quarantine = risk_int >= cfg.risk_quarantine_threshold

        results.append(
            AnalyzeResult(
                text_id=i,
                risk=risk_int,
                quarantine=quarantine,
                reasons=reasons,
                signals=AnalyzeSignals(
                    heuristic=float(h_score),
                    embedding=float(e_score),
                ),
            )
        )

    return AnalyzeResponse(results=results)


class ConfigResponse(BaseModel):
    """Response model for configuration endpoint."""
    heuristic_weight: float
    embedding_weight: float
    risk_quarantine_threshold: int


@app.get("/config", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    """Get current application configuration (read-only, sanitized).
    
    Returns:
        Sanitized configuration without secrets.
    
    Example:
        >>> # GET /config
        {
            "heuristic_weight": 0.4,
            "embedding_weight": 0.6,
            "risk_quarantine_threshold": 70
        }
    """
    try:
        from backend.utils.config import get_config as load_config
        cfg = load_config()
        
        return ConfigResponse(
            heuristic_weight=cfg.heuristic_weight,
            embedding_weight=cfg.embedding_weight,
            risk_quarantine_threshold=cfg.risk_quarantine_threshold,
        )
    except Exception as exc:
        logger.error("Failed to load config: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load configuration") from exc


@app.get("/metrics")
def metrics() -> Dict[str, Any]:
    """Prometheus-compatible metrics endpoint.
    
    Returns basic application metrics in a simple format.
    Can be extended with prometheus_client library for full Prometheus support.
    
    Returns:
        Dictionary with current metrics.
    """
    uptime = float(time.time() - _start_time)
    
    return {
        "uptime_seconds": uptime,
        "cache_size_heuristic": HEUR_CACHE.size(),
        "cache_size_embedding": EMB_CACHE.size(),
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    uptime = float(time.time() - _start_time)

    # Return package NAMES only (tests expect plain names like "fastapi")
    installed: List[str] = []
    try:
        import pkg_resources  # type: ignore
        names = sorted(
            {d.project_name for d in pkg_resources.working_set},
            key=lambda s: s.lower(),
        )
        # normalize to lowercase to make membership robust
        installed = [name.lower() for name in names]
    except Exception:
        installed = ["fastapi", "uvicorn", "scikit-learn", "numpy"]

    # Return a clean MAJOR.MINOR.MICRO version (digits only)
    vi = sys.version_info
    pyver = f"{vi.major}.{vi.minor}.{vi.micro}"

    return HealthResponse(
        status="ok",
        uptime_seconds=uptime,
        python_version=pyver,
        installed=installed[:200],
    )


# --- Batch Processing Storage ------------------------------------------------
# In-memory storage for batch results (could be Redis in production)
_BATCH_STORAGE: Dict[str, Dict[str, Any]] = {}
_MBOM_STORAGE: Dict[str, MBOMResponse] = {}


def _generate_batch_id() -> str:
    """Generate unique batch ID."""
    return f"batch_{uuid.uuid4().hex[:16]}"


def _sign_mbom(data: Dict[str, Any]) -> str:
    """Sign MBOM data with HMAC."""
    try:
        from backend.utils.config import get_config
        cfg = get_config()
        secret = cfg.hmac_secret.encode()
    except Exception:
        secret = b"default_secret_change_in_production"
    
    payload = json.dumps(data, sort_keys=True)
    signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    return signature


def _verify_mbom(mbom_doc: Dict[str, Any]) -> bool:
    """Verify MBOM signature.
    
    Args:
        mbom_doc: MBOM document with signature field.
    
    Returns:
        True if signature is valid, False otherwise.
    """
    if "signature" not in mbom_doc:
        return False
    
    stored_signature = mbom_doc["signature"]
    
    # Reconstruct signable payload
    payload = {
        "mbom_id": mbom_doc.get("mbom_id"),
        "batch_id": mbom_doc.get("batch_id"),
        "approved_by": mbom_doc.get("approved_by"),
        "timestamp": mbom_doc.get("timestamp"),
        "summary": mbom_doc.get("summary"),
        "results_hash": mbom_doc.get("results_hash"),
    }
    
    # Recompute signature
    expected_signature = _sign_mbom(payload)
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(stored_signature, expected_signature)


def _analyze_document(doc: DocumentInput, cfg) -> DocumentResult:
    """Analyze a single document and return result."""
    # Generate doc_id if not provided
    doc_id = doc.id or f"doc_{hashlib.md5(doc.content.encode()).hexdigest()[:12]}"
    
    # Check heuristic cache
    h_score = HEUR_CACHE.get(doc.content)
    if h_score is None:
        h_score, _ = _score_heuristic(doc.content)
        HEUR_CACHE.set(doc.content, h_score)
    
    # Check embedding cache
    e_score = EMB_CACHE.get(doc.content)
    if e_score is None:
        try:
            _initialize_detectors()
            if _detector:
                e_score = float(_detector.score([doc.content])[0])
            else:
                e_score = 0.0
        except Exception:
            e_score = 0.0
        EMB_CACHE.set(doc.content, e_score)
    
    # Calculate risk
    combined01 = _combine_signals(h_score, e_score)
    risk_int = _risk_to_int(combined01)
    
    # Build reasons
    reasons: List[str] = []
    reasons += reason_from_heur(h_score)
    reasons += reason_from_embed(e_score)
    _, h_reasons = _score_heuristic(doc.content)
    if h_reasons:
        reasons.extend(h_reasons)
    if "<script" in doc.content.lower():
        reasons.append("Possible HTML/JS injection content")
    
    # Deduplicate
    seen = set()
    deduped = []
    for reason in reasons:
        if reason not in seen:
            seen.add(reason)
            deduped.append(reason)
    
    # Determine action
    quarantine = risk_int >= cfg.risk_quarantine_threshold
    action = "quarantine" if quarantine else "allow"
    
    return DocumentResult(
        doc_id=doc_id,
        risk=risk_int,
        quarantine=quarantine,
        reasons=deduped,
        signals=AnalyzeSignals(heuristic=h_score, embedding=e_score),
        action=action,
    )


@app.post("/scan", response_model=ScanResponse)
def scan_documents(req: ScanRequest) -> ScanResponse:
    """Scan documents for threats with batch processing and pagination.
    
    Analyzes documents using heuristic and embedding detectors,
    returns per-document results with batch summary and suggested actions.
    
    Args:
        req: Scan request with documents and pagination parameters.
    
    Returns:
        Scan response with results, summary, and pagination info.
    
    Raises:
        HTTPException: If validation fails or processing errors occur.
    """
    try:
        from backend.utils.config import get_config
        cfg = get_config()
    except Exception as exc:
        logger.error("Config loading failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load configuration") from exc
    
    # Validate pagination
    start_idx = (req.page - 1) * req.page_size
    end_idx = start_idx + req.page_size
    
    if start_idx >= len(req.docs):
        raise HTTPException(status_code=400, detail="Page out of range")
    
    # Get page of documents
    page_docs = req.docs[start_idx:end_idx]
    total_pages = (len(req.docs) + req.page_size - 1) // req.page_size
    
    # Analyze documents
    results: List[DocumentResult] = []
    for doc in page_docs:
        try:
            result = _analyze_document(doc, cfg)
            results.append(result)
        except Exception as exc:
            logger.error(f"Failed to analyze document: {exc}")
            # Return error result for this document
            doc_id = doc.id or f"doc_error_{len(results)}"
            results.append(
                DocumentResult(
                    doc_id=doc_id,
                    risk=0,
                    quarantine=False,
                    reasons=[f"Analysis error: {str(exc)}"],
                    signals=AnalyzeSignals(heuristic=0.0, embedding=0.0),
                    action="allow",
                )
            )
    
    # Calculate summary
    quarantined = sum(1 for r in results if r.quarantine)
    allowed = len(results) - quarantined
    avg_risk = sum(r.risk for r in results) / len(results) if results else 0
    max_risk = max((r.risk for r in results), default=0)
    
    batch_id = _generate_batch_id()
    
    summary = BatchSummary(
        total_docs=len(req.docs),
        quarantined_count=quarantined,
        allowed_count=allowed,
        avg_risk=round(avg_risk, 2),
        max_risk=max_risk,
        batch_id=batch_id,
    )
    
    # Store batch results
    _BATCH_STORAGE[batch_id] = {
        "results": [r.dict() for r in results],
        "summary": summary.dict(),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset": req.dataset,
    }
    
    return ScanResponse(
        results=results,
        summary=summary,
        page=req.page,
        page_size=req.page_size,
        total_pages=total_pages,
    )


@app.post("/mbom", response_model=MBOMResponse)
def create_mbom(req: MBOMRequest) -> MBOMResponse:
    """Create signed Machine-readable Bill of Materials (MBOM).
    
    Generates a cryptographically signed MBOM document containing
    scan results and approval metadata.
    
    Args:
        req: MBOM request with approval info and results.
    
    Returns:
        Signed MBOM response with unique ID and signature.
    
    Raises:
        HTTPException: If validation or signing fails.
    """
    if not req.results:
        raise HTTPException(status_code=400, detail="Results cannot be empty")
    
    mbom_id = f"mbom_{uuid.uuid4().hex[:16]}"
    batch_id = req.batch_id or _generate_batch_id()
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Calculate summary
    quarantined = sum(1 for r in req.results if r.quarantine)
    allowed = len(req.results) - quarantined
    avg_risk = sum(r.risk for r in req.results) / len(req.results)
    
    summary_data = {
        "total_docs": len(req.results),
        "quarantined": quarantined,
        "allowed": allowed,
        "avg_risk": round(avg_risk, 2),
    }
    
    # Create signable payload
    payload = {
        "mbom_id": mbom_id,
        "batch_id": batch_id,
        "approved_by": req.approved_by,
        "timestamp": timestamp,
        "summary": summary_data,
        "results_hash": hashlib.sha256(
            json.dumps([r.dict() for r in req.results], sort_keys=True).encode()
        ).hexdigest(),
    }
    
    # Sign the MBOM
    signature = _sign_mbom(payload)
    
    mbom_response = MBOMResponse(
        mbom_id=mbom_id,
        batch_id=batch_id,
        approved_by=req.approved_by,
        timestamp=timestamp,
        results=req.results,
        signature=signature,
        summary=summary_data,
    )
    
    # Store MBOM
    _MBOM_STORAGE[mbom_id] = mbom_response
    
    return mbom_response


@app.get("/report/{batch_id}", response_model=ReportResponse)
def get_report(batch_id: str) -> ReportResponse:
    """Retrieve cached scan results and MBOM for a batch.
    
    Args:
        batch_id: Unique batch identifier.
    
    Returns:
        Report with results, summary, and MBOM if available.
    
    Raises:
        HTTPException: If batch_id not found (404).
    """
    if batch_id not in _BATCH_STORAGE:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    
    batch_data = _BATCH_STORAGE[batch_id]
    
    # Reconstruct models from stored dicts
    results = [DocumentResult(**r) for r in batch_data["results"]]
    summary = BatchSummary(**batch_data["summary"])
    
    # Find associated MBOM if any
    mbom = None
    for mbom_id, mbom_obj in _MBOM_STORAGE.items():
        if mbom_obj.batch_id == batch_id:
            mbom = mbom_obj
            break
    
    return ReportResponse(
        batch_id=batch_id,
        results=results,
        summary=summary,
        mbom=mbom,
        created_at=batch_data["created_at"],
    )
