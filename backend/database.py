"""
Database models and setup for API key management and usage tracking.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import secrets
import hashlib

Base = declarative_base()


class User(Base):
    """User account for API access."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Billing
    stripe_customer_id = Column(String, unique=True, index=True)
    subscription_tier = Column(String, default="free")  # free, pro, enterprise
    monthly_quota = Column(Integer, default=1000)  # API calls per month
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    usage_records = relationship("UsageRecord", back_populates="user")


class APIKey(Base):
    """API keys for authentication."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, unique=True, nullable=False, index=True)
    key_prefix = Column(String, nullable=False)  # First 8 chars for display (e.g., "sk_live_abc123...")
    name = Column(String, default="Default Key")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class UsageRecord(Base):
    """Track API usage per key."""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    
    # Usage details
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Billing metrics
    documents_scanned = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_cents = Column(Integer, default=0)  # Cost in cents
    
    # Performance
    response_time_ms = Column(Float)
    status_code = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="usage_records")


# Database setup
DATABASE_URL = "sqlite:///./sentineldf_api.db"  # Change to PostgreSQL in production

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.
    
    Returns:
        tuple: (full_key, key_hash, key_prefix)
        - full_key: The actual key to show user (only once!)
        - key_hash: Hashed version to store in database
        - key_prefix: First 8 chars for display (e.g., "sk_live_abc123...")
    """
    # Generate random key
    random_part = secrets.token_urlsafe(32)
    full_key = f"sk_live_{random_part}"
    
    # Hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    
    # Prefix for display
    key_prefix = full_key[:15] + "..."
    
    return full_key, key_hash, key_prefix


def hash_api_key(api_key: str) -> str:
    """Hash an API key for lookup."""
    return hashlib.sha256(api_key.encode()).hexdigest()


if __name__ == "__main__":
    # Initialize database
    init_db()
    print("Database tables created successfully!")
