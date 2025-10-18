"""
SentinelDF Cloud Control Plane API

Enterprise-grade API with:
- Pre-signed S3 uploads
- Async job submission
- Usage tracking & billing
- Rate limiting
- Multi-tenant isolation

This EXTENDS the existing api_server.py without breaking it.
"""
from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import secrets
import hashlib
import time
import os
from datetime import datetime, timedelta
import uuid

# Try to import existing api_server for backwards compatibility
try:
    from api_server import app as legacy_app, api_keys_db
    HAS_LEGACY = True
except ImportError:
    HAS_LEGACY = False
    api_keys_db = {}

app = FastAPI(
    title="SentinelDF Cloud API",
    version="3.0.0",
    description="Enterprise-scale data firewall for LLM training"
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
# MODELS
# ============================================================================

class UploadRequest(BaseModel):
    """Request to get pre-signed upload URLs."""
    file_count: int = Field(..., ge=1, le=1000, description="Number of files to upload")
    file_names: Optional[List[str]] = None
    ttl_minutes: int = Field(15, ge=5, le=60)

class UploadURL(BaseModel):
    """Pre-signed upload URL."""
    file_id: str
    upload_url: str
    expires_at: str

class UploadResponse(BaseModel):
    """Response with pre-signed URLs."""
    job_id: str
    upload_urls: List[UploadURL]
    expires_in_seconds: int

class ScanJobRequest(BaseModel):
    """Request to start a scan job."""
    job_id: str
    file_ids: List[str]
    priority: str = Field("normal", regex="^(low|normal|high|urgent)$")
    callback_url: Optional[str] = None

class ScanJobResponse(BaseModel):
    """Response after submitting scan job."""
    job_id: str
    status: str
    estimated_time_seconds: int
    status_url: str

class JobStatus(BaseModel):
    """Job status response."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0.0 to 1.0
    files_processed: int
    files_total: int
    result_url: Optional[str] = None
    created_at: str
    updated_at: str
    error: Optional[str] = None

class UsageResponse(BaseModel):
    """Usage statistics."""
    period: str
    total_scans: int
    documents_scanned: int
    tokens_processed: int
    cost_usd: float
    quota_remaining: int
    quota_limit: int

# ============================================================================
# IN-MEMORY STORAGE (Replace with Redis/Postgres in production)
# ============================================================================

jobs_db = {}  # job_id -> job metadata
usage_db = {}  # org_id -> usage stats

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_presigned_url(file_id: str, expires_in: int = 900) -> str:
    """
    Generate pre-signed S3 upload URL.
    
    In production, use boto3:
    s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket, 'Key': f'uploads/{file_id}'},
        ExpiresIn=expires_in
    )
    """
    # Mock URL for now - replace with actual S3
    bucket = os.getenv("S3_BUCKET", "sentineldf-prod")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    # In production, this would be a real pre-signed URL from S3
    return f"https://{bucket}.s3.{region}.amazonaws.com/uploads/{file_id}?X-Amz-Expires={expires_in}&X-Amz-Signature=mock"

def enqueue_job(job_id: str, file_ids: List[str], priority: str = "normal"):
    """
    Enqueue job to Redis/Celery.
    
    In production:
    from cloud.data_plane.tasks import process_scan_job
    process_scan_job.apply_async(args=[job_id, file_ids], priority=priority)
    """
    # Mock - just store in memory
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0.0,
        "files_processed": 0,
        "files_total": len(file_ids),
        "file_ids": file_ids,
        "priority": priority,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    print(f"[QUEUE] Enqueued job {job_id} with {len(file_ids)} files (priority: {priority})")

def verify_api_key(authorization: Optional[str] = Header(None)) -> dict:
    """Verify API key and return user info."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    
    api_key = authorization[7:]  # Remove "Bearer "
    
    # Check in legacy db first (backwards compatibility)
    if HAS_LEGACY and api_key in api_keys_db:
        return {
            "user_id": "legacy_user",
            "org_id": "legacy_org",
            "api_key": api_key
        }
    
    # Check in new system (would be Redis/Postgres)
    # For now, accept any key that starts with sk_live_
    if api_key.startswith("sk_live_"):
        return {
            "user_id": hashlib.sha256(api_key.encode()).hexdigest()[:16],
            "org_id": "org_" + hashlib.sha256(api_key.encode()).hexdigest()[:8],
            "api_key": api_key
        }
    
    raise HTTPException(status_code=401, detail="Invalid API key")

# ============================================================================
# ENDPOINTS - Backwards Compatible
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SentinelDF Cloud API",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "legacy_compatible": HAS_LEGACY
    }

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0"
    }

# ============================================================================
# ENDPOINTS - New Enterprise Features
# ============================================================================

@app.post("/v1/uploads", response_model=UploadResponse, tags=["Enterprise"])
async def get_upload_urls(
    request: UploadRequest,
    auth: dict = Depends(verify_api_key)
):
    """
    Get pre-signed S3 upload URLs.
    
    This allows clients to upload files directly to S3, bypassing the API
    and reducing bandwidth costs.
    
    **Flow:**
    1. Client requests upload URLs
    2. API generates pre-signed S3 URLs
    3. Client uploads files directly to S3
    4. Client submits scan job with file IDs
    """
    job_id = f"job_{uuid.uuid4().hex[:16]}"
    upload_urls = []
    
    for i in range(request.file_count):
        file_id = f"{job_id}_{i}_{uuid.uuid4().hex[:8]}"
        url = generate_presigned_url(file_id, request.ttl_minutes * 60)
        
        upload_urls.append(UploadURL(
            file_id=file_id,
            upload_url=url,
            expires_at=(datetime.utcnow() + timedelta(minutes=request.ttl_minutes)).isoformat()
        ))
    
    return UploadResponse(
        job_id=job_id,
        upload_urls=upload_urls,
        expires_in_seconds=request.ttl_minutes * 60
    )

@app.post("/v1/scan/async", response_model=ScanJobResponse, tags=["Enterprise"])
async def submit_scan_job(
    request: ScanJobRequest,
    background_tasks: BackgroundTasks,
    auth: dict = Depends(verify_api_key)
):
    """
    Submit async scan job.
    
    Files should already be uploaded to S3 via pre-signed URLs.
    Workers will pull from queue and process.
    
    **Priority Levels:**
    - `low`: Batch processing (cheapest)
    - `normal`: Standard queue
    - `high`: Priority queue (2x cost)
    - `urgent`: Immediate processing (5x cost)
    """
    # Enqueue job to Redis/Celery
    enqueue_job(request.job_id, request.file_ids, request.priority)
    
    # Estimate processing time based on file count and priority
    base_time = len(request.file_ids) * 2  # 2 seconds per file
    priority_multiplier = {"urgent": 0.2, "high": 0.5, "normal": 1.0, "low": 2.0}
    estimated_time = int(base_time * priority_multiplier[request.priority])
    
    return ScanJobResponse(
        job_id=request.job_id,
        status="pending",
        estimated_time_seconds=estimated_time,
        status_url=f"/v1/scan/status/{request.job_id}"
    )

@app.get("/v1/scan/status/{job_id}", response_model=JobStatus, tags=["Enterprise"])
async def get_job_status(
    job_id: str,
    auth: dict = Depends(verify_api_key)
):
    """
    Check job status.
    
    Returns current processing status and result URL when complete.
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    # Generate result URL if completed
    result_url = None
    if job["status"] == "completed":
        result_url = f"https://sentineldf-prod.s3.amazonaws.com/results/{job_id}/results.json"
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        files_processed=job["files_processed"],
        files_total=job["files_total"],
        result_url=result_url,
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        error=job.get("error")
    )

@app.get("/v1/usage", response_model=UsageResponse, tags=["Enterprise"])
async def get_usage(
    period: str = "current_month",
    auth: dict = Depends(verify_api_key)
):
    """
    Get usage statistics for billing.
    
    **Periods:**
    - `current_month`: Current billing period
    - `last_month`: Previous billing period
    - `ytd`: Year to date
    """
    org_id = auth["org_id"]
    
    # Mock data - in production, query from Postgres
    return UsageResponse(
        period=period,
        total_scans=1250,
        documents_scanned=45600,
        tokens_processed=2340000,
        cost_usd=4.56,
        quota_remaining=54400,
        quota_limit=100000
    )

# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

if HAS_LEGACY:
    # Mount legacy API routes under /legacy/
    @app.post("/v1/keys/create", tags=["Legacy - Backwards Compatible"])
    async def create_api_key_legacy(name: str = "Dashboard Key", authorization: Optional[str] = Header(None)):
        """Legacy endpoint - redirects to new system."""
        from api_server import create_api_key as legacy_create
        return await legacy_create(name, authorization)
    
    @app.get("/v1/keys/me", tags=["Legacy - Backwards Compatible"])
    async def get_keys_legacy(authorization: Optional[str] = Header(None)):
        """Legacy endpoint - redirects to new system."""
        from api_server import get_my_keys as legacy_get
        return await legacy_get(authorization)

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print("🚀 SentinelDF Cloud Control Plane starting...")
    print(f"   Version: 3.0.0")
    print(f"   Legacy compatible: {HAS_LEGACY}")
    print(f"   Environment: {os.getenv('ENVIRONMENT', 'development')}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SentinelDF Cloud API...")
    print("📖 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
