"""
Redis caching and queue configuration for SentinelDF Cloud.

Manages:
- Rate limiting (token bucket)
- API key caching
- Embedding cache (SHA256 deduplication)
- Job queue (Celery broker)
- Idempotency tracking
"""
import redis
import hashlib
import json
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import os

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Separate Redis DB for cache vs queue
CACHE_DB = 0
QUEUE_DB = 1

cache_client = redis.from_url(REDIS_URL.replace("/0", f"/{CACHE_DB}"), decode_responses=True)
queue_client = redis.from_url(REDIS_URL.replace("/0", f"/{QUEUE_DB}"), decode_responses=False)

# ============================================================================
# RATE LIMITING (Token Bucket Algorithm)
# ============================================================================

class RateLimiter:
    """
    Token bucket rate limiter using Redis.
    
    Allows burst traffic while maintaining average rate limits.
    """
    
    def __init__(self, client: redis.Redis = cache_client):
        self.client = client
    
    def check_rate_limit(
        self,
        key: str,
        max_tokens: int = 100,
        refill_rate: float = 1.0,  # tokens per second
        cost: int = 1
    ) -> tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Rate limit key (e.g., "ratelimit:org_123")
            max_tokens: Maximum bucket capacity
            refill_rate: Tokens added per second
            cost: Token cost of this request
        
        Returns:
            (allowed, metadata) where metadata includes remaining tokens
        """
        lua_script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local cost = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or max_tokens
        local last_update = tonumber(bucket[2]) or now
        
        -- Refill tokens based on time elapsed
        local elapsed = now - last_update
        tokens = math.min(max_tokens, tokens + (elapsed * refill_rate))
        
        -- Check if request can be satisfied
        local allowed = 0
        if tokens >= cost then
            tokens = tokens - cost
            allowed = 1
        end
        
        -- Update bucket state
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, 3600)  -- Expire after 1 hour of inactivity
        
        return {allowed, tokens, max_tokens}
        """
        
        now = time.time()
        result = self.client.eval(
            lua_script,
            1,
            key,
            max_tokens,
            refill_rate,
            cost,
            now
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        limit = int(result[2])
        
        metadata = {
            "limit": limit,
            "remaining": remaining,
            "reset_at": int(now + (limit - remaining) / refill_rate)
        }
        
        return allowed, metadata

# Global rate limiter instance
rate_limiter = RateLimiter()

# ============================================================================
# API KEY CACHING
# ============================================================================

def cache_api_key(key_hash: str, user_data: Dict[str, Any], ttl: int = 3600):
    """
    Cache API key validation result.
    
    Args:
        key_hash: Hashed API key
        user_data: User/org data
        ttl: Time to live in seconds
    """
    cache_key = f"apikey:{key_hash}"
    cache_client.setex(cache_key, ttl, json.dumps(user_data))

def get_cached_api_key(key_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached API key data."""
    cache_key = f"apikey:{key_hash}"
    data = cache_client.get(cache_key)
    return json.loads(data) if data else None

def invalidate_api_key(key_hash: str):
    """Invalidate cached API key."""
    cache_key = f"apikey:{key_hash}"
    cache_client.delete(cache_key)

# ============================================================================
# EMBEDDING CACHE (SHA256 Deduplication)
# ============================================================================

def get_text_hash(text: str) -> str:
    """Get SHA256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def cache_embedding(text: str, embedding: Any, ttl: int = 86400):
    """
    Cache embedding vector.
    
    Args:
        text: Input text
        embedding: Vector embedding or analysis result
        ttl: Time to live (default: 24 hours)
    """
    text_hash = get_text_hash(text)
    cache_key = f"embed:{text_hash}"
    
    # Store as JSON
    if isinstance(embedding, (dict, list)):
        cache_client.setex(cache_key, ttl, json.dumps(embedding))
    else:
        cache_client.setex(cache_key, ttl, str(embedding))

def get_cached_embedding(text: str) -> Optional[Any]:
    """Get cached embedding."""
    text_hash = get_text_hash(text)
    cache_key = f"embed:{text_hash}"
    
    data = cache_client.get(cache_key)
    if not data:
        return None
    
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return data

def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics."""
    total_keys = cache_client.dbsize()
    embed_keys = len(cache_client.keys("embed:*"))
    apikey_keys = len(cache_client.keys("apikey:*"))
    
    return {
        "total_keys": total_keys,
        "embedding_cache_size": embed_keys,
        "apikey_cache_size": apikey_keys
    }

# ============================================================================
# IDEMPOTENCY TRACKING
# ============================================================================

def check_idempotency_key(idempotency_key: str) -> Optional[Dict[str, Any]]:
    """
    Check if request with idempotency key was already processed.
    
    Returns cached response if duplicate request.
    """
    cache_key = f"idempotent:{idempotency_key}"
    data = cache_client.get(cache_key)
    return json.loads(data) if data else None

def store_idempotency_result(
    idempotency_key: str,
    result: Dict[str, Any],
    ttl: int = 86400
):
    """Store result for idempotency checking."""
    cache_key = f"idempotent:{idempotency_key}"
    cache_client.setex(cache_key, ttl, json.dumps(result))

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def create_session(user_id: str, data: Dict[str, Any], ttl: int = 3600) -> str:
    """Create user session."""
    session_id = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()
    cache_key = f"session:{session_id}"
    cache_client.setex(cache_key, ttl, json.dumps({
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        **data
    }))
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data."""
    cache_key = f"session:{session_id}"
    data = cache_client.get(cache_key)
    return json.loads(data) if data else None

def delete_session(session_id: str):
    """Delete session."""
    cache_key = f"session:{session_id}"
    cache_client.delete(cache_key)

# ============================================================================
# JOB STATUS TRACKING
# ============================================================================

def update_job_status(job_id: str, status: Dict[str, Any]):
    """Update job status in Redis."""
    cache_key = f"job:{job_id}"
    cache_client.setex(cache_key, 3600, json.dumps(status))

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status."""
    cache_key = f"job:{job_id}"
    data = cache_client.get(cache_key)
    return json.loads(data) if data else None

# ============================================================================
# HEALTH CHECK
# ============================================================================

def health_check() -> Dict[str, Any]:
    """Check Redis health."""
    try:
        cache_client.ping()
        queue_client.ping()
        
        stats = get_cache_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "cache_db": "connected",
            "queue_db": "connected",
            **stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================================
# INITIALIZATION
# ============================================================================

if __name__ == "__main__":
    print("🔴 Testing Redis Connection...")
    result = health_check()
    print(f"Status: {result['status']}")
    print(f"Stats: {result}")
