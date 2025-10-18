"""Persistent local cache for embeddings and heuristics using SQLite.

This provides deterministic, versioned caching with SHA-256 content hashing.
No external dependencies required - uses built-in sqlite3.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Cache schema version - increment to invalidate all cached entries
CACHE_SCHEMA_VERSION = 1

# Default cache directory
DEFAULT_CACHE_DIR = Path(".cache")


class PersistentCache:
    """SQLite-based persistent cache for detector results.
    
    Features:
    - Content-addressable storage (SHA-256 keys)
    - Schema versioning for invalidation
    - Separate tables for embeddings and heuristics
    - Cache hit/miss metrics
    
    Attributes:
        cache_dir: Path to cache directory.
        hits: Number of cache hits.
        misses: Number of cache misses.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize persistent cache.
        
        Args:
            cache_dir: Directory for cache database. Defaults to ./.cache/
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "sentineldf.db"
        self.hits = 0
        self.misses = 0
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            
            # Embeddings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    content_hash TEXT PRIMARY KEY,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    schema_version INTEGER NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            
            # Heuristics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS heuristics (
                    content_hash TEXT PRIMARY KEY,
                    score REAL NOT NULL,
                    reasons TEXT NOT NULL,
                    features TEXT,
                    detector_version TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            
            # Create indices for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_schema 
                ON embeddings(schema_version)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_heuristics_schema 
                ON heuristics(schema_version)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate SHA-256 hash of normalized content.
        
        Args:
            content: Text content to hash.
        
        Returns:
            Hex digest of SHA-256 hash.
        """
        # Normalize: strip whitespace, lowercase for consistent hashing
        normalized = content.strip().lower()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def get_embedding(
        self, 
        content: str, 
        model_name: str,
        model_version: str
    ) -> Optional[list[float]]:
        """Retrieve cached embedding if available.
        
        Args:
            content: Document content.
            model_name: Name of embedding model.
            model_version: Version of embedding model.
        
        Returns:
            Cached embedding vector or None if cache miss.
        """
        content_hash = self._hash_content(content)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT embedding FROM embeddings
                WHERE content_hash = ? 
                  AND model_name = ?
                  AND model_version = ?
                  AND schema_version = ?
            """, (content_hash, model_name, model_version, CACHE_SCHEMA_VERSION))
            
            row = cursor.fetchone()
            if row:
                self.hits += 1
                embedding = json.loads(row[0])
                logger.debug(f"Embedding cache HIT for hash {content_hash[:8]}...")
                return embedding
            else:
                self.misses += 1
                logger.debug(f"Embedding cache MISS for hash {content_hash[:8]}...")
                return None
        finally:
            conn.close()
    
    def set_embedding(
        self,
        content: str,
        model_name: str,
        model_version: str,
        embedding: list[float]
    ) -> None:
        """Store embedding in cache.
        
        Args:
            content: Document content.
            model_name: Name of embedding model.
            model_version: Version of embedding model.
            embedding: Embedding vector to cache.
        """
        content_hash = self._hash_content(content)
        embedding_json = json.dumps(embedding)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO embeddings 
                (content_hash, model_name, model_version, embedding, schema_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_hash, model_name, model_version, embedding_json, 
                  CACHE_SCHEMA_VERSION, time.time()))
            conn.commit()
            logger.debug(f"Cached embedding for hash {content_hash[:8]}...")
        finally:
            conn.close()
    
    def get_heuristic(
        self,
        content: str,
        detector_version: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached heuristic result if available.
        
        Args:
            content: Document content.
            detector_version: Version string of heuristic detector.
        
        Returns:
            Cached heuristic dict with score, reasons, features or None if cache miss.
        """
        content_hash = self._hash_content(content)
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT score, reasons, features FROM heuristics
                WHERE content_hash = ?
                  AND detector_version = ?
                  AND schema_version = ?
            """, (content_hash, detector_version, CACHE_SCHEMA_VERSION))
            
            row = cursor.fetchone()
            if row:
                self.hits += 1
                result = {
                    'score': row[0],
                    'reasons': json.loads(row[1]),
                    'features': json.loads(row[2]) if row[2] else None
                }
                logger.debug(f"Heuristic cache HIT for hash {content_hash[:8]}...")
                return result
            else:
                self.misses += 1
                logger.debug(f"Heuristic cache MISS for hash {content_hash[:8]}...")
                return None
        finally:
            conn.close()
    
    def set_heuristic(
        self,
        content: str,
        detector_version: str,
        score: float,
        reasons: list[str],
        features: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store heuristic result in cache.
        
        Args:
            content: Document content.
            detector_version: Version string of heuristic detector.
            score: Heuristic score.
            reasons: List of detection reasons.
            features: Optional feature dictionary.
        """
        content_hash = self._hash_content(content)
        reasons_json = json.dumps(reasons)
        features_json = json.dumps(features) if features else None
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO heuristics
                (content_hash, score, reasons, features, detector_version, schema_version, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (content_hash, score, reasons_json, features_json, detector_version,
                  CACHE_SCHEMA_VERSION, time.time()))
            conn.commit()
            logger.debug(f"Cached heuristic for hash {content_hash[:8]}...")
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with hits, misses, hit_rate, and total_entries.
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM embeddings WHERE schema_version = ?", 
                          (CACHE_SCHEMA_VERSION,))
            embedding_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM heuristics WHERE schema_version = ?",
                          (CACHE_SCHEMA_VERSION,))
            heuristic_count = cursor.fetchone()[0]
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'total_entries': embedding_count + heuristic_count,
                'embedding_entries': embedding_count,
                'heuristic_entries': heuristic_count
            }
        finally:
            conn.close()
    
    def clear(self) -> None:
        """Clear all cache entries."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embeddings")
            cursor.execute("DELETE FROM heuristics")
            conn.commit()
            logger.info("Cache cleared")
        finally:
            conn.close()
    
    def reset_metrics(self) -> None:
        """Reset hit/miss counters."""
        self.hits = 0
        self.misses = 0


# Global singleton instance
_cache_instance: Optional[PersistentCache] = None


def get_persistent_cache() -> PersistentCache:
    """Get or create the global persistent cache instance.
    
    Returns:
        Singleton PersistentCache instance.
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = PersistentCache()
    return _cache_instance
