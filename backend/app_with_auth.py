"""
Updated app.py with API key authentication integrated.

This shows how to add authentication to your existing endpoints.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from sqlalchemy.orm import Session

from backend.auth import verify_api_key, check_quota, track_usage
from backend.database import get_db, User, APIKey, init_db
from backend.api_keys_routes import router as keys_router

# Import your existing models and logic
from backend.app import (
    ScanRequest, ScanResponse, MBOMRequest, MBOMResponse,
    AnalyzeRequest, AnalyzeResponse, HealthResponse,
    app as original_app  # We'll modify this
)

# Initialize database on startup
init_db()

# Create new FastAPI app with authentication
app = FastAPI(
    title="SentinelDF API",
    version="2.0.0",
    description="Data Firewall for LLM Training - API as a Service"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API key management routes
app.include_router(keys_router)

# --- Public Endpoints (No Auth Required) ---

@app.get("/", tags=["Public"])
async def root():
    """Public root endpoint."""
    return {
        "service": "SentinelDF API",
        "version": "2.0.0",
        "docs": "/docs",
        "get_api_key": "POST /v1/keys/users with your email"
    }


@app.get("/health", response_model=HealthResponse, tags=["Public"])
async def health():
    """Health check endpoint (public)."""
    import sys
    return HealthResponse(
        status="healthy",
        uptime_seconds=time.time(),
        python_version=sys.version.split()[0],
        installed=["fastapi", "sqlalchemy", "pydantic"]
    )


# --- Protected Endpoints (Require API Key) ---

@app.post("/v1/scan", response_model=ScanResponse, tags=["Scanning"])
async def scan_documents_v1(
    request: ScanRequest,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Scan documents for threats (requires API key).
    
    **Authentication:**
    Include your API key in the Authorization header:
    ```
    Authorization: Bearer sk_live_your_key_here
    ```
    
    **Pricing:**
    - $0.01 per document scanned
    - Free tier: 1000 scans/month
    """
    user, api_key = auth
    
    # Check quota
    if not check_quota(user, db):
        raise HTTPException(
            status_code=429,
            detail=f"Monthly quota exceeded. Your limit: {user.monthly_quota} calls/month. Upgrade your plan to continue."
        )
    
    # Process scan using existing logic
    start_time = time.time()
    
    try:
        # Import the actual scan logic from your original app
        from backend.app import app as original_app
        # Call your existing scan endpoint logic
        # For now, we'll create a mock response - replace with actual logic
        
        from backend.app import _analyze_document, _generate_batch_id, BatchSummary, DocumentResult
        
        # Analyze documents
        results = []
        for doc in request.docs:
            result = _analyze_document(doc, {"quarantine_threshold": 70})
            results.append(result)
        
        # Calculate summary
        quarantined = sum(1 for r in results if r.quarantine)
        batch_id = _generate_batch_id()
        
        summary = BatchSummary(
            total_docs=len(request.docs),
            quarantined_count=quarantined,
            allowed_count=len(results) - quarantined,
            avg_risk=round(sum(r.risk for r in results) / len(results), 2) if results else 0,
            max_risk=max((r.risk for r in results), default=0),
            batch_id=batch_id
        )
        
        response = ScanResponse(
            results=results,
            summary=summary,
            page=request.page,
            page_size=request.page_size,
            total_pages=1
        )
        
        # Track usage for billing
        response_time_ms = (time.time() - start_time) * 1000
        track_usage(
            user=user,
            api_key=api_key,
            endpoint="/v1/scan",
            method="POST",
            documents_scanned=len(request.docs),
            tokens_used=sum(len(doc.content.split()) for doc in request.docs),
            response_time_ms=response_time_ms,
            status_code=200,
            db=db
        )
        
        return response
        
    except Exception as e:
        # Track failed request
        response_time_ms = (time.time() - start_time) * 1000
        track_usage(
            user=user,
            api_key=api_key,
            endpoint="/v1/scan",
            method="POST",
            documents_scanned=0,
            tokens_used=0,
            response_time_ms=response_time_ms,
            status_code=500,
            db=db
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_texts_v1(
    request: AnalyzeRequest,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Analyze texts for threats (requires API key).
    
    **Authentication:**
    ```
    Authorization: Bearer sk_live_your_key_here
    ```
    """
    user, api_key = auth
    
    if not check_quota(user, db):
        raise HTTPException(status_code=429, detail="Monthly quota exceeded")
    
    start_time = time.time()
    
    # Use your existing analyze logic
    from backend.app import _analyze_text
    
    results = []
    for i, text in enumerate(request.texts):
        result = _analyze_text(text, i, {"quarantine_threshold": 70})
        results.append(result)
    
    # Track usage
    response_time_ms = (time.time() - start_time) * 1000
    track_usage(
        user=user,
        api_key=api_key,
        endpoint="/v1/analyze",
        method="POST",
        documents_scanned=len(request.texts),
        tokens_used=sum(len(t.split()) for t in request.texts),
        response_time_ms=response_time_ms,
        status_code=200,
        db=db
    )
    
    return AnalyzeResponse(results=results)


@app.post("/v1/mbom", response_model=MBOMResponse, tags=["MBOM"])
async def create_mbom_v1(
    request: MBOMRequest,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Create signed MBOM (requires API key).
    """
    user, api_key = auth
    
    start_time = time.time()
    
    # Use your existing MBOM creation logic
    from backend.app import app as original_app
    # Call existing logic here
    
    # For now, mock response - replace with actual logic
    import uuid
    mbom_id = f"mbom_{uuid.uuid4().hex[:16]}"
    
    response = MBOMResponse(
        mbom_id=mbom_id,
        batch_id=request.batch_id or "batch_001",
        approved_by=request.approved_by,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        results=request.results,
        signature="mock_signature_replace_with_actual",
        summary={"total_docs": len(request.results)}
    )
    
    # Track usage
    response_time_ms = (time.time() - start_time) * 1000
    track_usage(
        user=user,
        api_key=api_key,
        endpoint="/v1/mbom",
        method="POST",
        documents_scanned=len(request.results),
        tokens_used=0,
        response_time_ms=response_time_ms,
        status_code=200,
        db=db
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SentinelDF API with authentication...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔑 Get API key: POST http://localhost:8000/v1/keys/users")
    uvicorn.run(app, host="0.0.0.0", port=8000)
