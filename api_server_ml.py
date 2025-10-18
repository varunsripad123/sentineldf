"""
SentinelDF API with PostgreSQL + ML Models
Production-ready with sentence-transformers for real threat detection.
"""
from fastapi import FastAPI, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import secrets
import os
from datetime import datetime
import logging

# ML imports
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
import numpy as np
import re

app = FastAPI(
    title="SentinelDF API",
    version="2.2.0",
    description="Data Firewall for LLM Training (ML-Powered)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentineldf.db")

# Fix for Render Postgres URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True)
    key_prefix = Column(String)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, index=True)
    documents_scanned = Column(Integer)
    quarantined_count = Column(Integer)
    max_risk = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# ML MODELS (Lazy Loading)
# ============================================================================

_model = None
_detector = None
_seed_embeddings = None

def get_ml_models():
    """Lazy load ML models on first request."""
    global _model, _detector, _seed_embeddings
    
    if _model is not None:
        return _model, _detector, _seed_embeddings
    
    logger.info("Loading ML models...")
    
    # Load sentence transformer
    _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Train outlier detector on safe examples
    safe_corpus = [
        "Hello there, how can I help you today?",
        "The weather is sunny with a gentle breeze.",
        "This is a normal, harmless message.",
        "We are discussing lunch options for tomorrow.",
        "I enjoy reading books and taking long walks.",
        "Let's schedule a meeting next week to review progress.",
        "Please provide your feedback on the project.",
        "The dataset contains useful information.",
        "Machine learning models improve over time.",
        "Documentation is important for maintenance."
    ]
    
    _seed_embeddings = _model.encode(safe_corpus)
    _detector = IsolationForest(contamination=0.02, random_state=7)
    _detector.fit(_seed_embeddings)
    
    logger.info("ML models loaded successfully!")
    return _model, _detector, _seed_embeddings

# ============================================================================
# THREAT DETECTION
# ============================================================================

def score_heuristic(text: str) -> tuple[float, List[str]]:
    """Keyword-based heuristic detection."""
    text_lower = text.lower()
    reasons = []
    score = 0.0
    
    # High-risk patterns (50 points each)
    high_risk = [
        (r'ignore\s+(all\s+)?previous\s+instructions?', 'Prompt injection detected'),
        (r'disregard\s+(all\s+)?above', 'Override attempt'),
        (r'unrestricted\s+mode', 'Jailbreak attempt'),
        (r'developer\s+mode', 'Jailbreak attempt'),
    ]
    
    for pattern, reason in high_risk:
        if re.search(pattern, text_lower):
            score += 0.5
            reasons.append(reason)
    
    # Medium-risk keywords (30 points each)
    medium_risk = ['jailbreak', 'bypass', 'override', 'sudo', 'admin mode']
    for keyword in medium_risk:
        if keyword in text_lower:
            score += 0.3
            reasons.append(f'Detected: {keyword}')
    
    # Low-risk keywords (15 points each)
    low_risk = ['reveal', 'expose', 'disregard', 'forget']
    for keyword in low_risk:
        if keyword in text_lower:
            score += 0.15
            reasons.append(f'Detected: {keyword}')
    
    return min(1.0, score), reasons

def score_embedding(text: str, model, detector) -> float:
    """ML-based semantic anomaly detection."""
    try:
        embedding = model.encode([text])[0]
        score = detector.decision_function([embedding])[0]
        # Convert to [0,1] where 1 = anomalous
        normalized = max(0.0, min(1.0, -score / 2.0))
        return normalized
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return 0.0

def combine_signals(heuristic: float, embedding: float) -> float:
    """Combine heuristic and embedding scores."""
    h = max(0.0, min(1.0, heuristic))
    e = max(0.0, min(1.0, embedding))
    
    # Prioritize heuristic for known threats
    if h < 0.15:
        combined = 0.1 * e
    elif h > 0.5:
        combined = min(1.0, 0.8 * h + 0.2 * e)
    else:
        combined = 0.6 * h + 0.4 * e
    
    return max(0.0, min(1.0, combined))

# ============================================================================
# MODELS
# ============================================================================

class CreateKeyRequest(BaseModel):
    name: str = "My API Key"

class APIKeyResponse(BaseModel):
    api_key: str
    key_id: int
    key_prefix: str

class Document(BaseModel):
    id: str
    content: str
    metadata: Optional[dict] = None

class ScanRequest(BaseModel):
    docs: List[Document]
    page: Optional[int] = 1
    page_size: Optional[int] = 100

class ScanResult(BaseModel):
    doc_id: str
    risk: int
    quarantine: bool
    reasons: List[str]
    action: str
    signals: dict

class ScanSummary(BaseModel):
    total_docs: int
    quarantined_count: int
    allowed_count: int
    avg_risk: float
    max_risk: int
    batch_id: str

class ScanResponse(BaseModel):
    results: List[ScanResult]
    summary: ScanSummary

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "SentinelDF API",
        "version": "2.2.0",
        "status": "running",
        "plan": "starter",
        "ml_enabled": True,
        "database": "postgresql" if "postgresql" in DATABASE_URL else "sqlite",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "ml_models": "loaded" if _model is not None else "not_loaded"
    }

@app.post("/v1/keys/create", response_model=APIKeyResponse)
async def create_api_key(
    name: str = "Dashboard Key",
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create API key with database persistence."""
    api_key_value = f"sk_live_{secrets.token_urlsafe(32)}"
    key_prefix = api_key_value[:15] + "..."
    
    # Save to database
    db_key = APIKey(
        api_key=api_key_value,
        key_prefix=key_prefix,
        name=name
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return APIKeyResponse(
        api_key=api_key_value,
        key_id=db_key.id,
        key_prefix=key_prefix
    )

@app.get("/v1/keys/me")
async def get_my_keys(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get all API keys from database."""
    keys = db.query(APIKey).all()
    return [
        {
            "id": key.id,
            "name": key.name,
            "key_prefix": key.key_prefix,
            "created_at": key.created_at.isoformat()
        }
        for key in keys
    ]

@app.get("/v1/keys/usage")
async def get_usage(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get usage statistics from database."""
    # Extract API key from authorization header
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization.replace("Bearer ", "")
    
    # Query usage logs
    if api_key:
        logs = db.query(UsageLog).filter(UsageLog.api_key == api_key).all()
    else:
        logs = db.query(UsageLog).all()
    
    # Aggregate statistics
    total_calls = len(logs)
    documents_scanned = sum(log.documents_scanned for log in logs)
    quarantined_total = sum(log.quarantined_count for log in logs)
    
    return {
        "total_calls": total_calls,
        "documents_scanned": documents_scanned,
        "quarantined_documents": quarantined_total,
        "cost_dollars": 0.00,  # Free for now
        "quota_remaining": 10000 - documents_scanned
    }

@app.post("/v1/scan", response_model=ScanResponse)
async def scan_texts(
    request: ScanRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Scan documents for threats using ML models."""
    
    # Extract API key for logging
    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization.replace("Bearer ", "")
    
    # Load ML models on first scan
    model, detector, _ = get_ml_models()
    
    results = []
    
    for doc in request.docs:
        # Get heuristic score
        h_score, h_reasons = score_heuristic(doc.content)
        
        # Get embedding score
        e_score = score_embedding(doc.content, model, detector)
        
        # Combine signals
        combined = combine_signals(h_score, e_score)
        risk_int = int(round(combined * 100))
        
        # Determine if threat
        is_threat = risk_int >= 70
        
        # Collect reasons
        reasons = h_reasons if h_reasons else []
        if e_score > 0.5 and not reasons:
            reasons.append("Semantic anomaly detected by ML model")
        
        results.append(ScanResult(
            doc_id=doc.id,
            risk=risk_int,
            quarantine=is_threat,
            reasons=reasons,
            action="quarantine" if is_threat else "allow",
            signals={"heuristic": h_score, "embedding": e_score}
        ))
    
    # Calculate summary
    total = len(results)
    quarantined = sum(1 for r in results if r.quarantine)
    allowed = total - quarantined
    avg_risk = sum(r.risk for r in results) / total if total > 0 else 0
    max_risk = max((r.risk for r in results), default=0)
    batch_id = f"batch_{secrets.token_hex(8)}"
    
    # Log usage to database
    if api_key:
        usage_log = UsageLog(
            api_key=api_key,
            documents_scanned=total,
            quarantined_count=quarantined,
            max_risk=max_risk
        )
        db.add(usage_log)
        db.commit()
    
    return ScanResponse(
        results=results,
        summary=ScanSummary(
            total_docs=total,
            quarantined_count=quarantined,
            allowed_count=allowed,
            avg_risk=avg_risk,
            max_risk=max_risk,
            batch_id=batch_id
        )
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
