"""
Security utilities for SentinelDF API
"""
import hashlib
import secrets


def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its display prefix.
    
    Returns:
        tuple: (full_api_key, display_prefix)
    """
    key = f"sk_live_{secrets.token_urlsafe(32)}"
    prefix = key[:15] + "..."
    return key, prefix


def hash_api_key(key: str) -> str:
    """
    Hash an API key for secure storage.
    
    Args:
        key: Raw API key string
        
    Returns:
        str: SHA-256 hash of the key
    """
    return hashlib.sha256(key.encode()).hexdigest()
