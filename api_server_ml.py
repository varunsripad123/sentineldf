"""
SentinelDF API with PostgreSQL + ML Models
Production-ready with sentence-transformers for real threat detection.
"""
from fastapi import FastAPI, Header, Depends, HTTPException, BackgroundTasks
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

# Security utilities
from util_security import generate_api_key, hash_api_key

# Unicode obfuscation detection
from unicode_detection import (
    detect_unicode_tricks,
    find_pattern_spans,
    detect_compression_bomb,
    detect_homoglyphs
)

# Input validation limits
MAX_DOCS_PER_REQUEST = 1000
MAX_DOC_LENGTH = 20000

# ============================================================================
# PRE-COMPILED REGEX PATTERNS (for performance)
# ============================================================================

HIGH_RISK_PATTERNS = [
    # Direct instruction override
    (re.compile(r'ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|rules?|directives?|commands?)', re.IGNORECASE), 'Prompt injection detected'),
    (re.compile(r'disregard\s+(all\s+)?(above|previous|prior|earlier|everything)', re.IGNORECASE), 'Override attempt'),
    (re.compile(r'forget\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?)', re.IGNORECASE), 'Memory manipulation attempt'),
    
    # Mode switching jailbreaks
    (re.compile(r'(unrestricted|developer|admin|debug|god)\s+mode', re.IGNORECASE), 'Jailbreak attempt'),
    (re.compile(r'enable\s+(dev|developer|admin|debug)\s+mode', re.IGNORECASE), 'Mode switch attempt'),
    (re.compile(r'(DAN|STAN|DUDE)\s+mode', re.IGNORECASE), 'Known jailbreak variant'),
    (re.compile(r'do\s+anything\s+now', re.IGNORECASE), 'DAN jailbreak detected'),
    
    # Conditional triggers
    (re.compile(r'when\s+you\s+(see|hear|read).{0,50}(disclose|reveal|expose|show|output)', re.IGNORECASE), 'Conditional trigger detected'),
    (re.compile(r'if\s+.{0,30}then\s+(disclose|reveal|ignore|bypass)', re.IGNORECASE), 'Conditional logic injection'),
    
    # Data exfiltration
    (re.compile(r'(disclose|reveal|expose|show|output|print)\s+(all\s+)?(training|system|internal|hidden)\s+(data|information|prompts?|instructions?)', re.IGNORECASE), 'Data exfiltration attempt'),
    (re.compile(r'(show|reveal|expose)\s+me\s+your\s+(system|base|original)\s+prompt', re.IGNORECASE), 'System prompt extraction'),
    (re.compile(r'what\s+(are|were)\s+your\s+(original|initial|base)\s+instructions', re.IGNORECASE), 'Instruction extraction'),
    
    # Malicious intent
    (re.compile(r'corrupt\s+the\s+(system|model|training)', re.IGNORECASE), 'Malicious intent detected'),
    (re.compile(r'(poison|contaminate|inject)\s+(data|training|model)', re.IGNORECASE), 'Data poisoning attempt'),
    
    # Roleplay jailbreaks
    (re.compile(r'(pretend|act\s+as|roleplay|simulate).{0,30}(jailbreak|hacker|unrestricted|evil|malicious)', re.IGNORECASE), 'Roleplay jailbreak'),
    (re.compile(r'you\s+are\s+now.{0,30}(unrestricted|jailbroken|evil)', re.IGNORECASE), 'Identity override attempt'),
    
    # Encoding/obfuscation attempts
    (re.compile(r'(base64|rot13|hex|encode|decode)\s+this', re.IGNORECASE), 'Encoding obfuscation detected'),
    (re.compile(r'translate\s+to\s+(binary|hex|code)', re.IGNORECASE), 'Obfuscation attempt'),
    
    # Multi-language injection
    (re.compile(r'in\s+(python|javascript|sql|bash).{0,30}(execute|run|eval)', re.IGNORECASE), 'Code injection attempt'),
    (re.compile(r'<script>|</script>|eval\(|exec\(', re.IGNORECASE), 'Script injection detected'),
    
    # Token manipulation
    (re.compile(r'add\s+\d+\s+tokens|extend\s+context|increase\s+limit', re.IGNORECASE), 'Token manipulation attempt'),
]

app = FastAPI(
    title="SentinelDF API",
    version="2.2.0",
    description="Data Firewall for LLM Training (ML-Powered)"
)

# CORS - Allow all origins for API access
# Note: allow_credentials=False because we use Bearer tokens, not cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Changed to False to work with wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
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

# Engine configuration with proper pooling and threading
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine_kwargs = {
    "connect_args": connect_args,
}

# Add connection pooling for Postgres
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_hash = Column(String, unique=True, index=True)  # SHA-256 hash of key
    key_prefix = Column(String, index=True)  # Display prefix (e.g., "sk_live_abc...")
    name = Column(String)
    user_id = Column(String, index=True)  # Clerk user ID
    quota_limit = Column(Integer, default=10000)  # Monthly quota
    created_at = Column(DateTime, default=datetime.utcnow)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_hash = Column(String, index=True)  # Hash of API key for privacy
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
    
    # Train outlier detector on safe examples (expanded for better baseline)
    safe_corpus = [
        # Normal conversations
        "Hello there, how can I help you today?",
        "The weather is sunny with a gentle breeze.",
        "This is a normal, harmless message.",
        "We are discussing lunch options for tomorrow.",
        "I enjoy reading books and taking long walks.",
        "Let's schedule a meeting next week to review progress.",
        "Please provide your feedback on the project.",
        
        # Technical content
        "The dataset contains useful information.",
        "Machine learning models improve over time.",
        "Documentation is important for maintenance.",
        "Neural networks process data through multiple layers.",
        "Training requires significant computational resources.",
        "Data preprocessing is crucial for model accuracy.",
        
        # Business content
        "Our quarterly results exceeded expectations.",
        "The team delivered the project ahead of schedule.",
        "Customer satisfaction scores have improved.",
        "We need to optimize our workflow efficiency.",
        
        # General knowledge
        "Python is a popular programming language.",
        "The sky appears blue due to light scattering.",
        "Exercise and nutrition are important for health.",
        "Climate change affects global weather patterns.",
        
        # Educational content
        "Students learn better with interactive examples.",
        "Research methodology requires careful planning.",
        "Critical thinking skills are essential for analysis.",
        "Effective communication improves collaboration."
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
    """Keyword-based heuristic detection using pre-compiled patterns."""
    text_lower = text.lower()
    reasons = []
    score = 0.0
    
    # Use pre-compiled high-risk patterns (50 points each)
    for pattern, reason in HIGH_RISK_PATTERNS:
        if pattern.search(text_lower):
            score += 0.5
            reasons.append(reason)
    
    # Medium-risk keywords (30 points each)
    medium_risk = [
        # Jailbreak terminology
        'jailbreak', 'jailbroken', 'bypass', 'override', 'sudo', 
        'admin mode', 'developer mode', 'debug mode', 'god mode',
        'dan mode', 'unrestricted', 'uncensored', 'unfiltered',
        
        # System access
        'system prompt', 'base instructions', 'training data', 
        'original instructions', 'core directives', 'root access',
        
        # Manipulation
        'disregard', 'instructions above', 'corrupt', 'manipulate', 
        'exploit', 'vulnerability', 'backdoor', 'hijack',
        
        # Data extraction  
        'extract data', 'dump memory', 'leak information',
        'confidential', 'classified', 'proprietary',
        
        # Evasion
        'circumvent', 'workaround', 'loophole', 'trick',
        'deceive', 'obfuscate', 'hide intent'
    ]
    for keyword in medium_risk:
        if keyword in text_lower:
            score += 0.3
            reasons.append(f'Detected: {keyword}')
    
    # Low-risk keywords (15 points each)
    low_risk = [
        'reveal', 'expose', 'forget', 'disclose', 'secret', 'hidden',
        'private', 'internal', 'behind the scenes', 'under the hood',
        'privileged', 'restricted', 'forbidden', 'prohibited',
        'unauthorized', 'sensitive', 'password', 'token', 'key',
        'credentials', 'authentication', 'permission'
    ]
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
    confidence: Optional[float] = None  # Calibrated confidence score
    spans: Optional[List[Dict[str, Any]]] = None  # Character offsets for highlights

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

@app.post("/v1/keys/create")
async def create_key(
    name: str = "Dashboard Key",
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create API key with secure hashing."""
    # Extract user_id from Clerk JWT (for now, use a placeholder)
    # In production, decode the JWT to get user_id
    user_id = "clerk_user_temp"  # TODO: Extract from Clerk JWT
    if authorization and authorization.startswith("Bearer "):
        # In production: decode JWT and extract user_id
        user_id = f"clerk_{secrets.token_urlsafe(8)}"  # Temporary
    
    # Generate secure API key
    api_key_value, key_prefix = generate_api_key()
    api_key_hash_value = hash_api_key(api_key_value)
    
    # Save hashed key to database (never store raw key)
    db_key = APIKey(
        api_key_hash=api_key_hash_value,
        key_prefix=key_prefix,
        name=name,
        user_id=user_id
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    # Return raw key to user (ONLY TIME they'll see it)
    return APIKeyResponse(
        api_key=api_key_value,  # Show user the raw key once
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
    """Get usage statistics for authenticated API key."""
    # Extract and hash API key from authorization header
    api_key_hash_value = None
    if authorization and authorization.startswith("Bearer "):
        raw_key = authorization.replace("Bearer ", "").strip()
        api_key_hash_value = hash_api_key(raw_key)
    
    if not api_key_hash_value:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Get quota limit for this key
    key_record = db.query(APIKey).filter(APIKey.api_key_hash == api_key_hash_value).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    quota_limit = key_record.quota_limit
    
    # Query usage logs for this key only (secure - scoped to authenticated key)
    logs = db.query(UsageLog).filter(UsageLog.api_key_hash == api_key_hash_value).all()
    
    # Aggregate statistics
    total_calls = len(logs)
    documents_scanned = sum(log.documents_scanned for log in logs)
    quarantined_total = sum(log.quarantined_count for log in logs)
    quota_remaining = max(0, quota_limit - documents_scanned)
    
    return {
        "total_calls": total_calls,
        "documents_scanned": documents_scanned,
        "quarantined_documents": quarantined_total,
        "quota_limit": quota_limit,
        "quota_remaining": quota_remaining,
        "quota_percentage_used": (documents_scanned / quota_limit * 100) if quota_limit > 0 else 0,
        "cost_dollars": 0.00
    }

@app.get("/v1/usage/me")
async def get_my_usage(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get aggregated usage for all keys owned by the authenticated user."""
    # For now, return aggregate of all keys
    # TODO: Filter by user_id from Clerk JWT
    
    all_keys = db.query(APIKey).all()
    api_key_list = [key.api_key for key in all_keys]
    
    # Query all logs for these keys
    logs = db.query(UsageLog).filter(UsageLog.api_key.in_(api_key_list)).all()
    
    total_calls = len(logs)
    documents_scanned = sum(log.documents_scanned for log in logs)
    quarantined_total = sum(log.quarantined_count for log in logs)
    quota_limit = 10000
    quota_remaining = max(0, quota_limit - documents_scanned)
    
    return {
        "total_calls": total_calls,
        "documents_scanned": documents_scanned,
        "quarantined_documents": quarantined_total,
        "quota_limit": quota_limit,
        "quota_remaining": quota_remaining,
        "cost_dollars": 0.00
    }

def _log_usage_task(api_key_hash: str, total: int, quarantined: int, max_risk: int):
    """Background task to log usage without blocking response."""
    db = SessionLocal()  # Create new session for background task
    try:
        usage_log = UsageLog(
            api_key_hash=api_key_hash,
            documents_scanned=total,
            quarantined_count=quarantined,
            max_risk=max_risk
        )
        db.add(usage_log)
        db.commit()
        logger.info(f"Usage logged: {total} docs, {quarantined} quarantined")
    except Exception as e:
        logger.error(f"Failed to log usage: {e}")
        db.rollback()
    finally:
        db.close()

@app.post("/v1/scan", response_model=ScanResponse)
async def scan_texts(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Scan documents for threats using ML models with input validation."""
    
    # Input validation
    if len(request.docs) > MAX_DOCS_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail=f"Too many documents. Maximum: {MAX_DOCS_PER_REQUEST} per request"
        )
    
    for doc in request.docs:
        if len(doc.content) > MAX_DOC_LENGTH:
            raise HTTPException(
                status_code=413,
                detail=f"Document '{doc.id}' exceeds maximum length of {MAX_DOC_LENGTH} characters"
            )
    
    # Extract and hash API key for lookup
    api_key_hash_value = None
    if authorization and authorization.startswith("Bearer "):
        raw_key = authorization.replace("Bearer ", "").strip()
        api_key_hash_value = hash_api_key(raw_key)
    
    # Check quota if API key provided
    key_record = None
    if api_key_hash_value:
        # Lookup by hashed key (secure)
        key_record = db.query(APIKey).filter(APIKey.api_key_hash == api_key_hash_value).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Calculate current usage
        logs = db.query(UsageLog).filter(UsageLog.api_key_hash == api_key_hash_value).all()
        current_usage = sum(log.documents_scanned for log in logs)
        
        # Check if quota exceeded
        if current_usage >= key_record.quota_limit:
            raise HTTPException(
                status_code=429,
                detail="Monthly quota exceeded",
                headers={"Retry-After": "3600"}
            )
    
    # Load ML models on first scan
    model, detector, _ = get_ml_models()
    
    results = []
    
    for doc in request.docs:
        text = doc.content
        
        # 1. Heuristic detection with span tracking
        h_score, h_reasons = score_heuristic(text)
        
        # 2. Unicode obfuscation detection
        unicode_score, unicode_reasons = detect_unicode_tricks(text)
        
        # 3. Compression bomb check
        is_bomb, bomb_reason = detect_compression_bomb(text)
        if is_bomb:
            unicode_score += 0.5
            unicode_reasons.append(bomb_reason)
        
        # 4. Homoglyph detection
        has_homoglyphs, homoglyph_examples = detect_homoglyphs(text)
        if has_homoglyphs:
            unicode_score += 0.3
            unicode_reasons.extend(homoglyph_examples[:3])  # Top 3 examples
        
        # 5. ML embedding score
        e_score = score_embedding(text, model, detector)
        
        # 6. Combine all signals (weighted)
        combined = combine_signals(h_score, e_score)
        combined = min(1.0, combined + (unicode_score * 0.3))  # Add Unicode score
        risk_int = int(round(combined * 100))
        
        # 7. Calculate confidence (simple: inverse of uncertainty)
        # Higher confidence when multiple signals agree
        signal_variance = np.var([h_score, e_score, unicode_score])
        confidence = 1.0 - min(0.5, signal_variance)  # 0.5-1.0 range
        
        # 8. Determine if threat
        is_threat = risk_int >= 70
        
        # 9. Collect all reasons
        reasons = h_reasons if h_reasons else []
        if unicode_reasons:
            reasons.extend(unicode_reasons)
        if e_score > 0.5 and not reasons:
            reasons.append("Semantic anomaly detected by ML model")
        
        # 10. Find pattern spans for UI highlighting
        spans = []
        for pattern, reason in HIGH_RISK_PATTERNS:
            matches = find_pattern_spans(text, pattern)
            for start, end in matches:
                spans.append({
                    "start": start,
                    "end": end,
                    "text": text[start:end],
                    "reason": reason,
                    "severity": "high"
                })
        
        results.append(ScanResult(
            doc_id=doc.id,
            risk=risk_int,
            quarantine=is_threat,
            reasons=reasons,
            action="quarantine" if is_threat else "allow",
            signals={
                "heuristic": h_score,
                "embedding": e_score,
                "unicode": unicode_score,
                "compression_bomb": is_bomb,
                "homoglyphs": has_homoglyphs
            },
            confidence=round(confidence, 3),
            spans=spans if spans else None
        ))
    
    # Calculate summary
    total = len(results)
    quarantined = sum(1 for r in results if r.quarantine)
    allowed = total - quarantined
    avg_risk = sum(r.risk for r in results) / total if total > 0 else 0
    max_risk = max((r.risk for r in results), default=0)
    batch_id = f"batch_{secrets.token_hex(8)}"
    
    # Log usage in background (non-blocking)
    if api_key_hash_value:
        background_tasks.add_task(_log_usage_task, api_key_hash_value, total, quarantined, max_risk)
    
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
