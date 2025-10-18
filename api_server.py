"""
Minimal FastAPI app for API key management.
Standalone file at root level for easy deployment.
"""
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import secrets
from datetime import datetime

app = FastAPI(
    title="SentinelDF API",
    version="2.0.0",
    description="Data Firewall for LLM Training"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
api_keys_db = {}

class CreateKeyRequest(BaseModel):
    name: str = "My API Key"

class APIKeyResponse(BaseModel):
    api_key: str
    key_id: int
    key_prefix: str

@app.get("/")
async def root():
    return {
        "service": "SentinelDF API",
        "version": "2.0.0",
        "status": "running",
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
    request: CreateKeyRequest,
    authorization: Optional[str] = Header(None)
):
    """Create a new API key."""
    api_key = f"sk_live_{secrets.token_urlsafe(32)}"
    key_id = len(api_keys_db) + 1
    key_prefix = api_key[:15] + "..."
    
    api_keys_db[api_key] = {
        "id": key_id,
        "name": request.name,
        "key_prefix": key_prefix,
        "created_at": datetime.utcnow().isoformat()
    }
    
    return APIKeyResponse(
        api_key=api_key,
        key_id=key_id,
        key_prefix=key_prefix
    )

@app.get("/v1/keys/me")
async def get_my_keys(authorization: Optional[str] = Header(None)):
    """Get all API keys."""
    keys = []
    for key, data in api_keys_db.items():
        keys.append({
            "id": data["id"],
            "name": data["name"],
            "key_prefix": data["key_prefix"],
            "created_at": data["created_at"]
        })
    return keys

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
