import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

from app.cache.redis_client import redis_client

logger = logging.getLogger(__name__)

REDIS_AVAILABLE = False
try:
    # Test Redis connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info("Redis connection established successfully")
except Exception as e:
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available: {e}. Using in-memory cache fallback.")


class CacheService:
    """
    Cache service with Redis support and in-memory fallback.
    """
    
    # In-memory cache as fallback when Redis is unavailable
    _memory_cache = {}
    _memory_ttl = {}
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Get value from cache.
        Tries Redis first, falls back to in-memory cache.
        """
        # Try Redis first if available
        if REDIS_AVAILABLE:
            try:
                value = redis_client.get(key)
                if value is not None:
                    return json.loads(value)
                return None
            except Exception as e:
                logger.warning(f"Redis get error: {e}. Falling back to memory cache.")
        
        # Fallback to in-memory cache
        try:
            if key in CacheService._memory_cache:
                # Check TTL
                if key in CacheService._memory_ttl:
                    if datetime.now() > CacheService._memory_ttl[key]:
                        # Expired
                        del CacheService._memory_cache[key]
                        del CacheService._memory_ttl[key]
                        return None
                return CacheService._memory_cache[key]
            return None
        except Exception as e:
            logger.error(f"Memory cache get error: {e}")
            return None
    
    @staticmethod
    def set(
        key: str,
        value: Any,
        ttl_seconds: int,
    ) -> bool:
        """
        Set value in cache with TTL.
        Tries Redis first, falls back to in-memory cache.
        Returns True if successful, False otherwise.
        """
        success = False
        
        # Try Redis first if available
        if REDIS_AVAILABLE:
            try:
                redis_client.set(
                    key,
                    json.dumps(value, default=str),
                    ex=ttl_seconds,
                )
                success = True
                logger.debug(f"Redis cache set: {key}")
            except Exception as e:
                logger.warning(f"Redis set error: {e}. Falling back to memory cache.")
        
        try:
            CacheService._memory_cache[key] = value
            CacheService._memory_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
            success = True
            logger.debug(f"Memory cache set: {key}")
        except Exception as e:
            logger.error(f"Memory cache set error: {e}")
        
        return success
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete value from cache.
        Returns True if successful, False otherwise.
        """
        success = False
        
        # Try Redis first if available
        if REDIS_AVAILABLE:
            try:
                redis_client.delete(key)
                success = True
                logger.debug(f"Redis cache deleted: {key}")
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # Delete from memory
        try:
            if key in CacheService._memory_cache:
                del CacheService._memory_cache[key]
            if key in CacheService._memory_ttl:
                del CacheService._memory_ttl[key]
            success = True
            logger.debug(f"Memory cache deleted: {key}")
        except Exception as e:
            logger.error(f"Memory delete error: {e}")
        
        return success
    
    @staticmethod
    def exists(key: str) -> bool:
        """
        Check if a key exists in cache.
        """
        # Check Redis first if available
        if REDIS_AVAILABLE:
            try:
                return bool(redis_client.exists(key))
            except Exception as e:
                logger.warning(f"Redis exists error: {e}")
        
        # Check memory cache
        try:
            if key in CacheService._memory_cache:
                # Check TTL
                if key in CacheService._memory_ttl:
                    if datetime.now() > CacheService._memory_ttl[key]:
                        # Expired
                        del CacheService._memory_cache[key]
                        del CacheService._memory_ttl[key]
                        return False
                return True
            return False
        except Exception as e:
            logger.error(f"Memory exists error: {e}")
            return False
    
    @staticmethod
    def invalidate_policy(
        policy_code: str,
        version: str,
    ) -> bool:
        """
        Invalidate a policy cache entry.
        """
        key = f"policy:{policy_code}:v{version}"
        return CacheService.delete(key)
    
    @staticmethod
    def clear() -> bool:
        """
        Clear all cache.
        """
        success = False
        
        # Clear Redis if available
        if REDIS_AVAILABLE:
            try:
                redis_client.flushdb()
                success = True
                logger.info("Redis cache cleared")
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        # Clear memory cache
        try:
            CacheService._memory_cache.clear()
            CacheService._memory_ttl.clear()
            success = True
            logger.info("Memory cache cleared")
        except Exception as e:
            logger.error(f"Memory clear error: {e}")
        
        return success
    
    @staticmethod
    def get_memory_cache_size() -> int:
        """
        Get the size of the in-memory cache (for debugging).
        """
        return len(CacheService._memory_cache)
    
    @staticmethod
    def get_memory_cache_keys() -> list:
        """
        Get all keys in the in-memory cache (for debugging).
        """
        return list(CacheService._memory_cache.keys())