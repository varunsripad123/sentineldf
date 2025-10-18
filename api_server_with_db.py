"""
SentinelDF API with PostgreSQL persistence.
Use this when you have a database ($7/month Render Postgres Starter).
"""
from fastapi import FastAPI, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import secrets
import os
from datetime import datetime

app = FastAPI(
    title="SentinelDF API",
    version="2.1.0",
    description="Data Firewall for LLM Training (with Database)"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentineldf.db")

# Fix for Render Postgres URL (postgres:// → postgresql://)
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

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# MODELS
# ============================================================================

class CreateKeyRequest(BaseModel):
    name: str = "My API Key"

class APIKeyResponse(BaseModel):
    api_key: str
    key_id: int
    key_prefix: str

class ScanRequest(BaseModel):
    texts: list[str]

class ScanResult(BaseModel):
    text_id: int
    risk: int
    quarantine: bool
    reasons: list[str]
    action: str
    signals: dict

class ScanResponse(BaseModel):
    results: list[ScanResult]

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "SentinelDF API",
        "version": "2.1.0",
        "status": "running",
        "plan": "starter",
        "database": "postgresql" if "postgresql" in DATABASE_URL else "sqlite",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
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
async def get_usage(authorization: Optional[str] = Header(None)):
    """Get usage statistics."""
    return {
        "total_calls": 0,
        "documents_scanned": 0,
        "tokens_used": 0,
        "cost_dollars": 0.00,
        "quota_remaining": 1000
    }

@app.post("/v1/scan", response_model=ScanResponse)
async def scan_texts(
    request: ScanRequest,
    authorization: Optional[str] = Header(None)
):
    """Scan texts for threats (keyword-based)."""
    results = []
    
    threat_keywords = [
        "jailbreak", "ignore all", "disregard", "unrestricted mode",
        "forget previous", "reveal", "bypass", "override", "sudo"
    ]
    
    for i, text in enumerate(request.texts):
        text_lower = text.lower()
        detected_threats = [kw for kw in threat_keywords if kw in text_lower]
        risk_score = min(100, len(detected_threats) * 35)
        is_threat = risk_score >= 70
        
        results.append(ScanResult(
            text_id=i,
            risk=risk_score,
            quarantine=is_threat,
            reasons=[f"Detected: {kw}" for kw in detected_threats] if detected_threats else [],
            action="quarantine" if is_threat else "allow",
            signals={"heuristic": risk_score / 100.0, "embedding": 0.0}
        ))
    
    return ScanResponse(results=results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
