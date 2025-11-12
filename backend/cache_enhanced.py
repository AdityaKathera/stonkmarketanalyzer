"""
Enhanced caching with Redis support and intelligent TTL
"""
import time
import json
import hashlib
from typing import Any, Optional, Dict
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not installed. Using memory cache only.")


class EnhancedCache:
    def __init__(self, redis_url=None, default_ttl=3600):
        """
        Initialize cache with optional Redis backend
        Falls back to in-memory if Redis unavailable
        """
        self.default_ttl = default_ttl
        self.memory_cache = {}  # Fallback
        
        # Try to connect to Redis
        self.redis_client = None
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                print("✓ Redis cache connected")
            except Exception as e:
                print(f"⚠️  Redis unavailable, using memory cache: {e}")
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent keys
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        hash_str = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_str}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self.hits += 1
                    return json.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            value, timestamp, ttl = self.memory_cache[key]
            if time.time() - timestamp < ttl:
                self.hits += 1
                return value
            else:
                del self.memory_cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # Fallback to memory cache
        self.memory_cache[key] = (value, time.time(), ttl)
    
    def delete(self, key: str):
        """Delete key from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def clear(self):
        """Clear all cache"""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass
        
        self.memory_cache.clear()
        self.hits = 0
        self.misses = 0
    
    def size(self):
        """Get cache size"""
        if self.redis_client:
            try:
                return self.redis_client.dbsize()
            except:
                pass
        return len(self.memory_cache)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'size': self.size(),
            'backend': 'redis' if self.redis_client else 'memory',
            'ttl': self.default_ttl
        }
    
    def cleanup_expired(self):
        """Remove expired entries from memory cache"""
        if self.redis_client:
            return 0  # Redis handles expiry automatically
        
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp, ttl) in self.memory_cache.items()
            if current_time - timestamp >= ttl
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        return len(expired_keys)


# Decorator for automatic caching
def cached(cache_instance, ttl=3600, key_prefix='api'):
    """
    Decorator to automatically cache function results
    
    Usage:
        @cached(response_cache, ttl=3600, key_prefix='stock_analysis')
        def analyze_stock(ticker, step):
            # ... expensive operation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = cache_instance._generate_key(
                f"{key_prefix}:{func.__name__}",
                args=str(args),
                kwargs=str(kwargs)
            )
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result:
                if isinstance(cached_result, dict):
                    cached_result['cached'] = True
                return cached_result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            if isinstance(result, dict):
                result['cached'] = False
                cache_instance.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
