"""
API Key management endpoints.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import (
    get_db, generate_api_key, User, APIKey, UsageRecord
)
from backend.auth import verify_api_key

router = APIRouter(prefix="/v1/keys", tags=["API Keys"])


# --- Request/Response Models ---

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    company: str = "Individual"


class CreateUserResponse(BaseModel):
    user_id: int
    email: str
    api_key: str  # Only shown once!
    message: str


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None
    is_active: bool
    rate_limit_per_minute: int


class UsageStatsResponse(BaseModel):
    total_calls: int
    documents_scanned: int
    tokens_used: int
    cost_dollars: float
    quota_remaining: int


# --- Endpoints ---

@router.post("/users", response_model=CreateUserResponse)
async def create_user_with_key(
    request: CreateUserRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new user and generate their first API key.
    
    **This is typically called from your landing page after beta signup.**
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user = User(
        email=request.email,
        name=request.name,
        company=request.company,
        subscription_tier="free",
        monthly_quota=1000  # 1000 free API calls per month
    )
    db.add(user)
    db.flush()
    
    # Generate API key
    full_key, key_hash, key_prefix = generate_api_key()
    
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name="Default API Key"
    )
    db.add(api_key)
    db.commit()
    
    return CreateUserResponse(
        user_id=user.id,
        email=user.email,
        api_key=full_key,  # ⚠️ Only shown once!
        message="API key created successfully. Save it now - you won't see it again!"
    )


@router.get("/me", response_model=List[APIKeyResponse])
async def list_my_keys(
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the authenticated user.
    """
    user, _ = auth
    
    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    
    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            is_active=key.is_active,
            rate_limit_per_minute=key.rate_limit_per_minute
        )
        for key in keys
    ]


@router.post("/create", response_model=dict)
async def create_additional_key(
    name: str,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Create an additional API key for the authenticated user.
    """
    user, _ = auth
    
    # Generate new key
    full_key, key_hash, key_prefix = generate_api_key()
    
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name
    )
    db.add(api_key)
    db.commit()
    
    return {
        "api_key": full_key,  # ⚠️ Only shown once!
        "key_prefix": key_prefix,
        "message": "API key created successfully. Save it now!"
    }


@router.delete("/{key_id}")
async def revoke_key(
    key_id: int,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key (soft delete).
    """
    user, _ = auth
    
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"}


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the current billing period.
    """
    user, _ = auth
    
    # Get current month's usage
    from sqlalchemy import func, extract
    now = datetime.utcnow()
    
    usage = db.query(
        func.count(UsageRecord.id).label('total_calls'),
        func.sum(UsageRecord.documents_scanned).label('documents_scanned'),
        func.sum(UsageRecord.tokens_used).label('tokens_used'),
        func.sum(UsageRecord.cost_cents).label('cost_cents')
    ).filter(
        UsageRecord.user_id == user.id,
        extract('year', UsageRecord.timestamp) == now.year,
        extract('month', UsageRecord.timestamp) == now.month
    ).first()
    
    total_calls = usage.total_calls or 0
    documents_scanned = usage.documents_scanned or 0
    tokens_used = usage.tokens_used or 0
    cost_cents = usage.cost_cents or 0
    
    return UsageStatsResponse(
        total_calls=total_calls,
        documents_scanned=documents_scanned,
        tokens_used=tokens_used,
        cost_dollars=cost_cents / 100.0,
        quota_remaining=max(0, user.monthly_quota - total_calls)
    )
