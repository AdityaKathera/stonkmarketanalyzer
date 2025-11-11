"""
Simple in-memory cache for API responses
"""
import time
from typing import Any, Optional

class SimpleCache:
    def __init__(self, ttl_seconds=3600):
        """
        Initialize cache with time-to-live in seconds
        Default: 1 hour (3600 seconds)
        """
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Expired, remove it
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache with current timestamp"""
        self.cache[key] = (value, time.time())
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def size(self):
        """Get number of cached items"""
        return len(self.cache)
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        return len(expired_keys)
