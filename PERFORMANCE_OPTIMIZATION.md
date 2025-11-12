# ⚡ Performance Optimization Guide - Reducing API Latency

## 🔍 Current Performance Analysis

### Issues Identified:
1. **Cache exists but not fully utilized** - Only used in compare endpoint
2. **No cache for guided research** - Most common use case
3. **No cache for chat queries** - Second most common
4. **In-memory cache only** - Lost on restart
5. **No streaming responses** - User waits for full response
6. **No request deduplication** - Multiple users requesting same stock

### Current Latency:
- Perplexity API: 3-8 seconds per request
- No cache: Every request hits API
- User experience: Poor (long waits)

## 🚀 Solution: Multi-Layer Caching Strategy

### Layer 1: Smart In-Memory Cache (Immediate Win)
**Impact**: 80% latency reduction for cached requests
**Effort**: Low (1-2 hours)
**Cost**: Free

### Layer 2: Redis Cache (Persistent)
**Impact**: 90% latency reduction + survives restarts
**Effort**: Medium (4-6 hours)
**Cost**: $10-30/month

### Layer 3: Response Streaming (Perceived Performance)
**Impact**: Feels 3x faster (progressive loading)
**Effort**: Medium (4-6 hours)
**Cost**: Free

### Layer 4: Request Deduplication (Efficiency)
**Impact**: Reduces API costs by 30-50%
**Effort**: Low (2-3 hours)
**Cost**: Free

### Layer 5: CDN for Static Content
**Impact**: 50% faster page loads
**Effort**: Low (already using CloudFront)
**Cost**: Already paid

## 📋 Implementation Plan

### Phase 1: Quick Wins (Today - 2 hours)

#### 1. Add Caching to All Endpoints

**Current**: Only compare endpoint uses cache
**Fix**: Add cache to guided research and chat

**Benefits**:
- 80% faster for repeated queries
- Reduced API costs
- Better user experience

**Implementation**: See code below

#### 2. Increase Cache TTL Strategically

**Current**: 1 hour TTL for everything
**Fix**: Different TTL for different data types

```python
# Stock fundamentals: 24 hours (changes slowly)
# News/sentiment: 1 hour (changes frequently)
# Technical analysis: 4 hours (moderate)
```

#### 3. Add Cache Warming

**Current**: Cold cache on restart
**Fix**: Pre-populate cache with popular stocks

**Benefits**:
- Fast response for common stocks (AAPL, TSLA, etc.)
- Better first-user experience

### Phase 2: Redis Integration (This Week - 4 hours)

#### Why Redis?
- Persistent (survives restarts)
- Shared across instances (horizontal scaling)
- Fast (sub-millisecond reads)
- Built-in TTL management
- Supports complex data structures

#### Setup:
```bash
# Install Redis
sudo yum install redis -y

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Install Python client
pip install redis
```

### Phase 3: Response Streaming (Next Week - 4 hours)

#### Why Streaming?
- User sees results immediately
- Perceived latency: 10x better
- Better UX (progressive loading)
- Modern feel

#### How it works:
```
Traditional: [Wait 5s] → [Show all content]
Streaming:   [Show header] → [Stream content] → [Done]
             ↑ Instant      ↑ Progressive    ↑ 5s total
```

### Phase 4: Advanced Optimizations (Future)

1. **Request Deduplication**: If 10 users request AAPL simultaneously, only 1 API call
2. **Predictive Caching**: Pre-fetch likely next queries
3. **Partial Caching**: Cache individual research steps
4. **Background Refresh**: Update cache before expiry

## 💻 Code Implementation

### Enhanced Cache with Redis Support

```python
# backend/cache_enhanced.py
"""
Enhanced caching with Redis support and intelligent TTL
"""
import time
import json
import hashlib
from typing import Any, Optional, Dict
import redis
from functools import wraps

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
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
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
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        size = 0
        if self.redis_client:
            try:
                size = self.redis_client.dbsize()
            except:
                pass
        else:
            size = len(self.memory_cache)
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'size': size,
            'backend': 'redis' if self.redis_client else 'memory'
        }

# Decorator for automatic caching
def cached(ttl=3600, key_prefix='api'):
    """
    Decorator to automatically cache function results
    
    Usage:
        @cached(ttl=3600, key_prefix='stock_analysis')
        def analyze_stock(ticker, step):
            # ... expensive operation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result['cached'] = True
                return cached_result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            if isinstance(result, dict):
                result['cached'] = False
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache instance
cache = None

def init_cache(redis_url=None, default_ttl=3600):
    """Initialize global cache"""
    global cache
    cache = EnhancedCache(redis_url, default_ttl)
    return cache
```

### Updated App with Smart Caching

```python
# backend/app.py (additions)

from cache_enhanced import init_cache, cached

# Initialize enhanced cache
# Use Redis if available, fallback to memory
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
response_cache = init_cache(redis_url, default_ttl=3600)

# Cache TTL strategy
CACHE_TTL = {
    'fundamentals': 86400,  # 24 hours (changes slowly)
    'news': 3600,           # 1 hour (changes frequently)
    'technical': 14400,     # 4 hours (moderate)
    'chat': 1800,           # 30 minutes (conversational)
    'comparison': 7200,     # 2 hours (moderate)
}

@app.route('/api/research/guided', methods=['POST'])
@track_performance('/api/research/guided')
def guided_research():
    """Execute a guided research step with caching"""
    try:
        data = request.json
        step = data.get('step')
        ticker = data.get('ticker', '').upper()
        horizon = data.get('horizon', '1-3 years')
        risk_level = data.get('riskLevel', 'moderate')
        
        if not ticker or step not in prompt_templates:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Generate cache key
        cache_key = response_cache._generate_key(
            'guided',
            ticker=ticker,
            step=step,
            horizon=horizon,
            risk=risk_level
        )
        
        # Check cache
        cached_result = response_cache.get(cache_key)
        if cached_result:
            print(f"[CACHE HIT] {ticker} - {step}")
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        print(f"[CACHE MISS] {ticker} - {step}")
        
        # Get TTL based on step type
        step_category = prompt_templates[step].get('category', 'technical')
        ttl = CACHE_TTL.get(step_category, 3600)
        
        # Call API
        template_func = prompt_templates[step]['template']
        prompt = template_func(ticker, horizon, risk_level)
        response = perplexity_service.query(prompt)
        
        result = {
            'step': step,
            'ticker': ticker,
            'response': response['content'],
            'citations': response.get('citations', []),
            'cached': False
        }
        
        # Cache result
        response_cache.set(cache_key, result, ttl)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/chat', methods=['POST'])
@track_performance('/api/research/chat')
def free_chat():
    """Handle free-form chat with caching"""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper()
        question = data.get('question', '')
        
        if not ticker or not question:
            return jsonify({'error': 'Invalid request'}), 400
        
        # Generate cache key
        cache_key = response_cache._generate_key(
            'chat',
            ticker=ticker,
            question=question
        )
        
        # Check cache
        cached_result = response_cache.get(cache_key)
        if cached_result:
            print(f"[CACHE HIT] Chat: {ticker}")
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        print(f"[CACHE MISS] Chat: {ticker}")
        
        # Call API
        prompt = free_chat_template(ticker, question)
        response = perplexity_service.query(prompt)
        
        result = {
            'ticker': ticker,
            'question': question,
            'response': response['content'],
            'citations': response.get('citations', []),
            'cached': False
        }
        
        # Cache for 30 minutes
        response_cache.set(cache_key, result, CACHE_TTL['chat'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cache warming on startup
def warm_cache():
    """Pre-populate cache with popular stocks"""
    popular_stocks = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
    print("🔥 Warming cache with popular stocks...")
    
    # This would run in background
    # For now, just log
    print(f"   Will cache: {', '.join(popular_stocks)}")

# Call on startup
warm_cache()
```

## 📊 Expected Performance Improvements

### Before Optimization:
- First request: 5-8 seconds
- Repeated request: 5-8 seconds (no cache)
- Cache hit rate: ~20% (only compare endpoint)
- User experience: Poor

### After Phase 1 (Memory Cache):
- First request: 5-8 seconds
- Repeated request: <100ms (cached)
- Cache hit rate: ~60-70%
- User experience: Good

### After Phase 2 (Redis):
- First request: 5-8 seconds
- Repeated request: <50ms (Redis)
- Cache hit rate: ~80-85%
- Survives restarts: Yes
- User experience: Excellent

### After Phase 3 (Streaming):
- Perceived latency: <1 second
- Actual latency: Same
- User experience: Feels instant

## 🎯 Additional Latency Optimizations

### 1. Parallel API Calls
For multi-step research, call APIs in parallel:
```python
import asyncio

async def analyze_stock_parallel(ticker):
    tasks = [
        fetch_fundamentals(ticker),
        fetch_news(ticker),
        fetch_technical(ticker)
    ]
    results = await asyncio.gather(*tasks)
    return combine_results(results)
```

### 2. Request Deduplication
If multiple users request same stock simultaneously:
```python
pending_requests = {}  # ticker -> Future

def deduplicate_request(ticker):
    if ticker in pending_requests:
        return pending_requests[ticker]  # Wait for existing
    
    future = call_api(ticker)
    pending_requests[ticker] = future
    return future
```

### 3. Predictive Caching
Pre-fetch likely next queries:
```python
# User analyzed AAPL fundamentals
# Likely next: AAPL news, AAPL technical
# Pre-fetch in background
```

### 4. Compress Responses
Reduce network transfer time:
```python
from flask import Flask
from flask_compress import Compress

app = Flask(__name__)
Compress(app)  # Automatic gzip compression
```

### 5. CDN for API (Advanced)
Cache API responses at edge locations:
- Use CloudFront in front of API
- Cache GET requests
- Invalidate on updates

## 📈 Monitoring Cache Performance

Add to admin portal:
```python
@app.route(f'/api/{PORTAL_PATH}/cache/stats', methods=['GET'])
@require_auth
def cache_stats():
    stats = response_cache.get_stats()
    return jsonify(stats)
```

Shows:
- Hit rate %
- Total hits/misses
- Cache size
- Backend type (Redis/Memory)

## 🚀 Quick Start: Implement Today

### Step 1: Create Enhanced Cache (15 min)
```bash
# Create the file
touch backend/cache_enhanced.py
# Copy code from above
```

### Step 2: Update App (30 min)
```bash
# Update backend/app.py
# Add caching to guided_research and free_chat
```

### Step 3: Test (15 min)
```bash
# Test same query twice
curl -X POST https://api.stonkmarketanalyzer.com/api/research/guided \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL","step":"overview"}'

# Second call should be instant (cached)
```

### Step 4: Deploy (10 min)
```bash
# Upload to EC2
./deployment/deploy-comprehensive-analytics-v2.sh
```

## 💰 Cost Savings

### Current (No Cache):
- 1000 requests/day × $0.001 = $1/day
- Monthly: $30

### With 70% Cache Hit Rate:
- 300 API calls/day × $0.001 = $0.30/day
- Monthly: $9
- **Savings: $21/month (70%)**

### With 85% Cache Hit Rate (Redis):
- 150 API calls/day × $0.001 = $0.15/day
- Monthly: $4.50
- **Savings: $25.50/month (85%)**

## 🎯 Recommended Action Plan

### Today (2 hours):
1. ✅ Create `cache_enhanced.py`
2. ✅ Add caching to guided research
3. ✅ Add caching to chat
4. ✅ Deploy to EC2
5. ✅ Test and verify

### This Week (4 hours):
1. Install Redis on EC2
2. Update cache to use Redis
3. Add cache warming
4. Monitor performance

### Next Week (4 hours):
1. Implement response streaming
2. Add request deduplication
3. Optimize TTL strategy
4. Add cache metrics to admin portal

---

**Bottom Line**: Implementing smart caching will make your app feel 10x faster, reduce API costs by 70-85%, and significantly improve user experience. Start with Phase 1 today - it's a 2-hour investment for massive returns.

