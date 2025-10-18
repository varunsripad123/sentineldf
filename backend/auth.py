"""
API Key authentication and management.
"""
from datetime import datetime
from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db, hash_api_key, APIKey, User, UsageRecord


async def verify_api_key(
    authorization: str = Header(..., description="API key in format: Bearer sk_live_xxx"),
    db: Session = Depends(get_db)
) -> tuple[User, APIKey]:
    """
    Verify API key from Authorization header.
    
    Returns:
        tuple: (user, api_key) if valid
        
    Raises:
        HTTPException: If key is invalid or inactive
    """
    # Extract key from "Bearer sk_live_xxx" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Bearer sk_live_xxx"
        )
    
    api_key_str = authorization.replace("Bearer ", "").strip()
    
    if not api_key_str.startswith("sk_live_"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format. Keys should start with sk_live_"
        )
    
    # Hash and lookup
    key_hash = hash_api_key(api_key_str)
    
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    if not api_key.is_active:
        raise HTTPException(
            status_code=401,
            detail="API key has been revoked"
        )
    
    # Get user
    user = db.query(User).filter(User.id == api_key.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User account is inactive"
        )
    
    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return user, api_key


def check_quota(user: User, db: Session) -> bool:
    """
    Check if user has remaining quota for this month.
    
    Returns:
        bool: True if user has quota remaining
    """
    # Count usage this month
    from sqlalchemy import func, extract
    now = datetime.utcnow()
    
    monthly_usage = db.query(func.count(UsageRecord.id)).filter(
        UsageRecord.user_id == user.id,
        extract('year', UsageRecord.timestamp) == now.year,
        extract('month', UsageRecord.timestamp) == now.month
    ).scalar()
    
    return monthly_usage < user.monthly_quota


def track_usage(
    user: User,
    api_key: APIKey,
    endpoint: str,
    method: str,
    documents_scanned: int,
    tokens_used: int,
    response_time_ms: float,
    status_code: int,
    db: Session
):
    """
    Track API usage for billing and analytics.
    """
    # Calculate cost (example pricing)
    # $0.01 per document scanned
    cost_cents = documents_scanned * 1
    
    usage_record = UsageRecord(
        user_id=user.id,
        api_key_id=api_key.id,
        endpoint=endpoint,
        method=method,
        documents_scanned=documents_scanned,
        tokens_used=tokens_used,
        cost_cents=cost_cents,
        response_time_ms=response_time_ms,
        status_code=status_code
    )
    
    db.add(usage_record)
    db.commit()


# Optional: Simple API key for testing (no Bearer prefix)
async def verify_api_key_simple(
    x_api_key: str = Header(..., description="API key"),
    db: Session = Depends(get_db)
) -> tuple[User, APIKey]:
    """Alternative: Accept API key via X-API-Key header."""
    key_hash = hash_api_key(x_api_key)
    
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not api_key or not api_key.is_active:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    user = db.query(User).filter(User.id == api_key.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account inactive")
    
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return user, api_key
