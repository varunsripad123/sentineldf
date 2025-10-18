"""
SentinelDF Cloud Data Plane - Distributed Workers

High-throughput job processing with:
- Celery for job queue
- ONNX Runtime for fast ML inference
- SHA256 caching for deduplication
- Batch processing for efficiency
- S3 for result storage

This is SEPARATE from existing backend - no conflicts!
"""
from celery import Celery, Task
from typing import List, Dict, Any
import hashlib
import time
import json
import os
from datetime import datetime

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "sentineldf_workers",
    broker=redis_url,
    backend=redis_url
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Priority queues
celery_app.conf.task_routes = {
    'cloud.data_plane.worker.process_scan_job': {
        'queue': 'normal',
    },
}

# ============================================================================
# CACHING LAYER
# ============================================================================

embedding_cache = {}  # SHA256 -> embedding vector (in production: Redis)

def get_text_hash(text: str) -> str:
    """Get SHA256 hash of text for caching."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get_cached_embedding(text_hash: str) -> Any:
    """Get cached embedding if exists."""
    return embedding_cache.get(text_hash)

def cache_embedding(text_hash: str, embedding: Any):
    """Cache embedding for future use."""
    embedding_cache[text_hash] = embedding

# ============================================================================
# ML INFERENCE (Placeholder - will use ONNX)
# ============================================================================

def load_onnx_model():
    """
    Load ONNX INT8 quantized model.
    
    In production:
    import onnxruntime as ort
    sess = ort.InferenceSession("model_int8.onnx", providers=['CPUExecutionProvider'])
    return sess
    """
    print("[WORKER] Loading ONNX model (mock)...")
    return {"model": "mock"}

# Global model (loaded once per worker)
MODEL = None

def get_model():
    """Get or load model."""
    global MODEL
    if MODEL is None:
        MODEL = load_onnx_model()
    return MODEL

def analyze_text_batch(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze batch of texts using ML model.
    
    This is a placeholder - in production, it would:
    1. Check SHA256 cache
    2. Run ONNX inference
    3. Cache results
    4. Return risk scores
    """
    results = []
    
    for i, text in enumerate(texts):
        text_hash = get_text_hash(text)
        
        # Check cache first
        cached = get_cached_embedding(text_hash)
        if cached:
            print(f"[CACHE HIT] Document {i}")
            results.append(cached)
            continue
        
        # Mock ML inference
        risk_score = 50  # Would be from ONNX model
        if "jailbreak" in text.lower() or "ignore" in text.lower():
            risk_score = 95
        
        result = {
            "doc_id": f"doc_{i}",
            "risk": risk_score,
            "quarantine": risk_score >= 70,
            "reasons": ["Potential prompt injection"] if risk_score >= 70 else [],
            "action": "quarantine" if risk_score >= 70 else "allow",
            "signals": {
                "heuristic": risk_score / 100.0,
                "embedding": risk_score / 100.0
            }
        }
        
        # Cache result
        cache_embedding(text_hash, result)
        results.append(result)
    
    return results

# ============================================================================
# CELERY TASKS
# ============================================================================

class CallbackTask(Task):
    """Base task with callbacks."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds."""
        print(f"[SUCCESS] Task {task_id} completed")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails."""
        print(f"[FAILURE] Task {task_id} failed: {exc}")

@celery_app.task(base=CallbackTask, bind=True, name='process_scan_job')
def process_scan_job(self, job_id: str, file_ids: List[str], priority: str = "normal"):
    """
    Process a scan job.
    
    Steps:
    1. Download files from S3 (pre-signed URLs)
    2. Extract text content
    3. Batch analyze (up to 256 docs per batch)
    4. Upload results to S3
    5. Update job status
    
    Args:
        job_id: Unique job identifier
        file_ids: List of file IDs in S3
        priority: Job priority level
    """
    print(f"[WORKER] Processing job {job_id} with {len(file_ids)} files (priority: {priority})")
    
    # Update job status to processing
    self.update_state(
        state='PROCESSING',
        meta={'progress': 0.0, 'files_processed': 0, 'files_total': len(file_ids)}
    )
    
    try:
        # Step 1: Download files from S3
        texts = download_files_from_s3(file_ids)
        
        # Step 2: Batch process (256 docs at a time)
        batch_size = 256
        all_results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = analyze_text_batch(batch)
            all_results.extend(batch_results)
            
            # Update progress
            progress = min((i + len(batch)) / len(texts), 1.0)
            self.update_state(
                state='PROCESSING',
                meta={'progress': progress, 'files_processed': i + len(batch), 'files_total': len(texts)}
            )
            
            print(f"[PROGRESS] {int(progress * 100)}% complete ({i + len(batch)}/{len(texts)} files)")
        
        # Step 3: Generate summary
        quarantined_count = sum(1 for r in all_results if r['quarantine'])
        summary = {
            "total_docs": len(all_results),
            "quarantined_count": quarantined_count,
            "allowed_count": len(all_results) - quarantined_count,
            "avg_risk": sum(r['risk'] for r in all_results) / len(all_results),
            "max_risk": max(r['risk'] for r in all_results),
            "batch_id": job_id
        }
        
        # Step 4: Upload results to S3
        result_data = {
            "job_id": job_id,
            "status": "completed",
            "results": all_results,
            "summary": summary,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        upload_results_to_s3(job_id, result_data)
        
        print(f"[COMPLETE] Job {job_id} finished: {quarantined_count}/{len(all_results)} quarantined")
        
        return result_data
        
    except Exception as e:
        print(f"[ERROR] Job {job_id} failed: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

def download_files_from_s3(file_ids: List[str]) -> List[str]:
    """
    Download files from S3.
    
    In production:
    import boto3
    s3 = boto3.client('s3')
    for file_id in file_ids:
        obj = s3.get_object(Bucket='sentineldf-prod', Key=f'uploads/{file_id}')
        content = obj['Body'].read().decode('utf-8')
        texts.append(content)
    """
    # Mock data for now
    print(f"[S3] Downloading {len(file_ids)} files...")
    return [f"Sample text content for {fid}" for fid in file_ids]

def upload_results_to_s3(job_id: str, results: Dict[str, Any]):
    """
    Upload results to S3.
    
    In production:
    import boto3
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='sentineldf-prod',
        Key=f'results/{job_id}/results.json',
        Body=json.dumps(results),
        ContentType='application/json'
    )
    """
    print(f"[S3] Uploading results for job {job_id}...")
    # Mock - would actually upload to S3

# ============================================================================
# WORKER HEALTH CHECK
# ============================================================================

@celery_app.task(name='health_check')
def health_check():
    """Simple health check task."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": "sentineldf-worker",
        "cache_size": len(embedding_cache)
    }

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting SentinelDF Data Plane Worker...")
    print(f"   Redis: {redis_url}")
    print(f"   Cache size: {len(embedding_cache)}")
    
    # Start worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--max-tasks-per-child=1000'
    ])
