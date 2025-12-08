"""
Caching System for FlowSentinel
================================
Multi-layer caching with Redis and in-memory fallback.

Features:
- Redis-based distributed caching
- In-memory LRU cache fallback
- Cache invalidation strategies
- TTL-based expiration
- Cache statistics and monitoring
- Automatic serialization

Architecture:
- CacheBackend: Abstract interface
- RedisCache: Redis-based distributed cache
- MemoryCache: In-memory LRU cache
- MultiLevelCache: L1 (memory) + L2 (Redis)
- CacheManager: Central cache orchestration
"""

import logging
import hashlib
import json
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
from functools import wraps
import os

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class CacheConfig:
    """Cache configuration."""
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: float = 5.0
    
    # Memory cache settings
    MEMORY_MAX_SIZE: int = 10000
    MEMORY_DEFAULT_TTL: int = 300  # 5 minutes
    
    # Cache behavior
    DEFAULT_TTL: int = 3600  # 1 hour
    KEY_PREFIX: str = "flowsentinel:"
    ENABLE_COMPRESSION: bool = True
    COMPRESSION_THRESHOLD: int = 1024  # bytes
    
    # Statistics
    ENABLE_STATS: bool = True


# ============================================================================
# Cache Entry
# ============================================================================

@dataclass
class CacheEntry:
    """A cached value with metadata."""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    size_bytes: int = 0
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    @property
    def ttl_remaining(self) -> int:
        return max(0, int(self.expires_at - time.time()))


# ============================================================================
# Cache Backend Interface
# ============================================================================

class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached values."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


# ============================================================================
# In-Memory LRU Cache
# ============================================================================

class MemoryCache(CacheBackend):
    """
    In-memory LRU cache implementation.
    Thread-safe with asyncio lock.
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            if entry.is_expired:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            # Update LRU order
            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats["hits"] += 1
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache."""
        async with self._lock:
            ttl = ttl or self.config.MEMORY_DEFAULT_TTL
            now = time.time()
            
            # Serialize to estimate size
            try:
                serialized = json.dumps(value)
                size_bytes = len(serialized.encode())
            except (TypeError, ValueError):
                size_bytes = 0
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=now + ttl,
                size_bytes=size_bytes
            )
            
            # Evict if at capacity
            while len(self._cache) >= self.config.MEMORY_MAX_SIZE:
                self._cache.popitem(last=False)
                self._stats["evictions"] += 1
            
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._stats["sets"] += 1
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats["deletes"] += 1
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        entry = self._cache.get(key)
        return entry is not None and not entry.is_expired
    
    async def clear(self) -> bool:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        total_size = sum(e.size_bytes for e in self._cache.values())
        
        return {
            "type": "memory",
            "entries": len(self._cache),
            "max_size": self.config.MEMORY_MAX_SIZE,
            "total_size_bytes": total_size,
            "hit_rate": round(hit_rate, 2),
            **self._stats
        }
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values at once."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, mapping: Dict[str, Any], ttl: int = None) -> bool:
        """Set multiple values at once."""
        for key, value in mapping.items():
            await self.set(key, value, ttl)
        return True


# ============================================================================
# Redis Cache (with fallback)
# ============================================================================

class RedisCache(CacheBackend):
    """
    Redis-based distributed cache.
    Falls back to memory cache if Redis is unavailable.
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._redis = None
        self._fallback = MemoryCache(config)
        self._connected = False
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
            "fallback_uses": 0
        }
    
    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            # Import redis only if available
            import redis.asyncio as redis
            
            self._redis = redis.from_url(
                self.config.REDIS_URL,
                max_connections=self.config.REDIS_MAX_CONNECTIONS,
                socket_timeout=self.config.REDIS_SOCKET_TIMEOUT
            )
            
            # Test connection
            await self._redis.ping()
            self._connected = True
            logger.info("Connected to Redis")
            return True
            
        except ImportError:
            logger.warning("Redis package not installed, using memory cache")
            self._connected = False
            return False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using memory cache")
            self._connected = False
            return False
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.config.KEY_PREFIX}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self._connected:
            self._stats["fallback_uses"] += 1
            return await self._fallback.get(key)
        
        try:
            redis_key = self._make_key(key)
            value = await self._redis.get(redis_key)
            
            if value is None:
                self._stats["misses"] += 1
                return None
            
            self._stats["hits"] += 1
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._stats["errors"] += 1
            self._stats["fallback_uses"] += 1
            return await self._fallback.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache."""
        ttl = ttl or self.config.DEFAULT_TTL
        
        if not self._connected:
            self._stats["fallback_uses"] += 1
            return await self._fallback.set(key, value, ttl)
        
        try:
            redis_key = self._make_key(key)
            serialized = json.dumps(value)
            
            await self._redis.setex(redis_key, ttl, serialized)
            self._stats["sets"] += 1
            
            # Also set in memory cache for L1
            await self._fallback.set(key, value, min(ttl, 60))
            
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            self._stats["errors"] += 1
            self._stats["fallback_uses"] += 1
            return await self._fallback.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        # Always delete from memory cache
        await self._fallback.delete(key)
        
        if not self._connected:
            return True
        
        try:
            redis_key = self._make_key(key)
            await self._redis.delete(redis_key)
            self._stats["deletes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            self._stats["errors"] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._connected:
            return await self._fallback.exists(key)
        
        try:
            redis_key = self._make_key(key)
            return await self._redis.exists(redis_key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return await self._fallback.exists(key)
    
    async def clear(self) -> bool:
        """Clear all cached values."""
        await self._fallback.clear()
        
        if not self._connected:
            return True
        
        try:
            # Delete all keys with prefix
            pattern = f"{self.config.KEY_PREFIX}*"
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        memory_stats = await self._fallback.get_stats()
        
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "type": "redis",
            "connected": self._connected,
            "redis_url": self.config.REDIS_URL.split("@")[-1] if "@" in self.config.REDIS_URL else self.config.REDIS_URL,
            "hit_rate": round(hit_rate, 2),
            "memory_cache": memory_stats,
            **self._stats
        }


# ============================================================================
# Cache Manager
# ============================================================================

class CacheManager:
    """
    Central cache management with decorators and utilities.
    
    Usage:
        cache = CacheManager()
        
        # Manual caching
        await cache.set("key", {"data": "value"}, ttl=3600)
        data = await cache.get("key")
        
        # Decorator
        @cache.cached(ttl=300)
        async def get_data(id: str):
            return expensive_operation(id)
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self._backend: CacheBackend = MemoryCache(config)
        self._initialized = False
    
    async def initialize(self, use_redis: bool = True) -> None:
        """Initialize cache with appropriate backend."""
        if use_redis:
            redis_cache = RedisCache(self.config)
            if await redis_cache.connect():
                self._backend = redis_cache
            else:
                logger.info("Using memory cache as fallback")
        
        self._initialized = True
        logger.info(f"Cache initialized with {type(self._backend).__name__}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        return await self._backend.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache."""
        return await self._backend.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        return await self._backend.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self._backend.exists(key)
    
    async def clear(self) -> bool:
        """Clear all cached values."""
        return await self._backend.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return await self._backend.get_stats()
    
    def cached(
        self,
        ttl: int = None,
        key_prefix: str = "",
        key_builder: Callable = None
    ):
        """
        Decorator to cache function results.
        
        Usage:
            @cache.cached(ttl=300, key_prefix="user:")
            async def get_user(user_id: str):
                return db.get_user(user_id)
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    key_parts = [key_prefix, func.__name__]
                    key_parts.extend(str(a) for a in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = ":".join(key_parts)
                
                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: int = None
    ) -> Any:
        """
        Get value from cache, or compute and cache if missing.
        
        Usage:
            value = await cache.get_or_set(
                "expensive_key",
                lambda: compute_expensive_value(),
                ttl=3600
            )
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl)
        return value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        # This is a simplified version - Redis backend would use SCAN
        count = 0
        if isinstance(self._backend, MemoryCache):
            keys_to_delete = [
                k for k in self._backend._cache.keys()
                if pattern.replace("*", "") in k
            ]
            for key in keys_to_delete:
                await self.delete(key)
                count += 1
        return count


# ============================================================================
# Global Instance
# ============================================================================

_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create the global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


async def init_cache_manager(
    config: CacheConfig = None,
    use_redis: bool = True
) -> CacheManager:
    """Initialize the global cache manager."""
    global _cache_manager
    _cache_manager = CacheManager(config)
    await _cache_manager.initialize(use_redis)
    return _cache_manager
