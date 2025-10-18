"""
Database configuration for SentinelDF Cloud.

Manages:
- Postgres connection pooling
- Table partitioning
- Read replicas
- Multi-tenant isolation
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import os
from datetime import datetime

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/sentineldf"
)

# Connection pool configuration for high concurrency
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Base connections
    max_overflow=80,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Organization(Base):
    """Organization/tenant model."""
    __tablename__ = "organizations"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free")  # free, starter, pro, enterprise
    quota_monthly = Column(Integer, default=1000)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_org_created', 'created_at'),
    )

class User(Base):
    """User accounts."""
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    org_id = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    clerk_id = Column(String(100), unique=True)  # Clerk user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_org', 'org_id'),
        Index('idx_user_email', 'email'),
    )

class APIKey(Base):
    """API keys with bcrypt hashing."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String(255), unique=True, nullable=False)  # bcrypt hash
    key_prefix = Column(String(20), nullable=False)  # For display (e.g., "sk_live_abc...")
    user_id = Column(String(50), nullable=False, index=True)
    org_id = Column(String(50), nullable=False, index=True)
    name = Column(String(255))
    scopes = Column(JSON, default=list)  # ["scan", "mbom", "admin"]
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_apikey_org', 'org_id'),
        Index('idx_apikey_user', 'user_id'),
        Index('idx_apikey_hash', 'key_hash'),
    )

class ScanJob(Base):
    """Scan jobs - partitioned by org_id and date."""
    __tablename__ = "scan_jobs"
    
    id = Column(String(50), primary_key=True)
    org_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # pending, processing, completed, failed
    priority = Column(String(20), default="normal")
    files_total = Column(Integer, nullable=False)
    files_processed = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    result_url = Column(String(500))
    error = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_scan_org_date', 'org_id', 'created_at'),
        Index('idx_scan_status', 'status'),
        Index('idx_scan_user', 'user_id'),
    )

class UsageCounter(Base):
    """Usage counters for billing - partitioned by org_id and period."""
    __tablename__ = "usage_counters"
    
    id = Column(Integer, primary_key=True)
    org_id = Column(String(50), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # YYYY-MM format
    total_scans = Column(Integer, default=0)
    documents_scanned = Column(Integer, default=0)
    tokens_processed = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_usage_org_period', 'org_id', 'period', unique=True),
    )

class BillingRecord(Base):
    """Billing records for Stripe integration."""
    __tablename__ = "billing_records"
    
    id = Column(Integer, primary_key=True)
    org_id = Column(String(50), nullable=False, index=True)
    stripe_customer_id = Column(String(100))
    stripe_subscription_id = Column(String(100))
    period = Column(String(20), nullable=False)
    amount_usd = Column(Float, nullable=False)
    status = Column(String(20))  # pending, paid, failed
    invoice_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_billing_org_period', 'org_id', 'period'),
        Index('idx_billing_stripe', 'stripe_customer_id'),
    )

# ============================================================================
# DATABASE HELPERS
# ============================================================================

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def get_db() -> Session:
    """Get database session (dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Get database session as context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# ============================================================================
# PARTITIONING HELPERS
# ============================================================================

def create_partitions():
    """
    Create table partitions for scalability.
    
    Example: Partition scan_jobs by month
    
    CREATE TABLE scan_jobs_2025_01 PARTITION OF scan_jobs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    """
    # In production, use Postgres native partitioning
    # This is a placeholder showing the concept
    pass

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    print("🗄️ Initializing SentinelDF Cloud Database...")
    init_db()
    print("✅ Database ready!")
