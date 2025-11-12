from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib

from services.perplexity_service import PerplexityService
from services.stock_price_service import stock_price_service
from prompts.templates import prompt_templates, free_chat_template
from analytics import AnalyticsService
from analytics_comprehensive import ComprehensiveAnalytics
from secure_portal import setup_portal_routes
from cache import SimpleCache
from cache_enhanced import EnhancedCache
from auth_routes import auth_bp
import time
from functools import wraps

load_dotenv()

app = Flask(__name__)

# Configure CORS with environment-based origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=allowed_origins)

# Register authentication blueprint
app.register_blueprint(auth_bp)

perplexity_service = PerplexityService(os.getenv('PERPLEXITY_API_KEY'))
# Use comprehensive analytics for admin portal
analytics_service = ComprehensiveAnalytics()

# Initialize enhanced cache with Redis support (falls back to memory)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
response_cache = EnhancedCache(redis_url=redis_url, default_ttl=3600)

# Cache TTL strategy (in seconds)
CACHE_TTL = {
    'fundamentals': 86400,  # 24 hours - changes slowly
    'news': 3600,           # 1 hour - changes frequently  
    'technical': 14400,     # 4 hours - moderate
    'chat': 1800,           # 30 minutes - conversational
    'comparison': 7200,     # 2 hours - moderate
    'overview': 14400,      # 4 hours
}

# Performance tracking decorator
def track_performance(endpoint_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                status_code = result[1] if isinstance(result, tuple) else 200
                analytics_service.track_api_call(endpoint_name, duration_ms, status_code)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                analytics_service.track_api_call(endpoint_name, duration_ms, 500)
                analytics_service.track_error('api_error', str(e))
                raise
        return decorated_function
    return decorator

# Setup secure admin portal
portal_path, portal_username = setup_portal_routes(app, analytics_service)
print(f"🔒 Secure portal initialized at: /api/{portal_path}")
print(f"🔑 Portal username: {portal_username}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Stock Research API is running'})

@app.route('/api/research/guided', methods=['POST'])
@track_performance('/api/research/guided')
def guided_research():
    """Execute a guided research step with intelligent caching"""
    try:
        data = request.json
        step = data.get('step')
        ticker = data.get('ticker', '').upper()
        horizon = data.get('horizon', '1-3 years')
        risk_level = data.get('riskLevel', 'moderate')
        
        print(f"[DEBUG] Guided research request: step={step}, ticker={ticker}")
        
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400
        
        if step not in prompt_templates:
            return jsonify({'error': f'Invalid step: {step}'}), 400
        
        # Generate cache key
        cache_key = response_cache._generate_key(
            'guided',
            ticker=ticker,
            step=step,
            horizon=horizon,
            risk=risk_level
        )
        
        # Check cache first
        cached_result = response_cache.get(cache_key)
        if cached_result:
            print(f"[CACHE HIT] {ticker} - {step}")
            analytics_service.track_cache(hit=True)
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        print(f"[CACHE MISS] {ticker} - {step} - Calling API...")
        analytics_service.track_cache(hit=False)
        
        # Get the prompt template and inject user inputs
        template_func = prompt_templates[step]['template']
        prompt = template_func(ticker, horizon, risk_level)
        
        # Call Perplexity API
        response = perplexity_service.query(prompt)
        
        print(f"[DEBUG] API call successful")
        
        result = {
            'step': step,
            'ticker': ticker,
            'response': response['content'],
            'citations': response.get('citations', []),
            'cached': False
        }
        
        # Determine TTL based on step type
        ttl = CACHE_TTL.get(step, 3600)  # Default 1 hour
        
        # Cache the result
        response_cache.set(cache_key, result, ttl)
        print(f"[CACHE SET] {ticker} - {step} (TTL: {ttl}s)")
        
        return jsonify(result)
    
    except Exception as e:
        print(f"[ERROR] Guided research failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/chat', methods=['POST'])
@track_performance('/api/research/chat')
def free_chat():
    """Handle free-form chat queries with caching"""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper()
        question = data.get('question', '')
        
        if not ticker or not question:
            return jsonify({'error': 'Ticker and question are required'}), 400
        
        # Generate cache key
        cache_key = response_cache._generate_key(
            'chat',
            ticker=ticker,
            question=question
        )
        
        # Check cache first
        cached_result = response_cache.get(cache_key)
        if cached_result:
            print(f"[CACHE HIT] Chat: {ticker}")
            analytics_service.track_cache(hit=True)
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        print(f"[CACHE MISS] Chat: {ticker} - Calling API...")
        analytics_service.track_cache(hit=False)
        
        # Generate prompt for free chat
        prompt = free_chat_template(ticker, question)
        
        # Call Perplexity API
        response = perplexity_service.query(prompt)
        
        result = {
            'ticker': ticker,
            'question': question,
            'response': response['content'],
            'citations': response.get('citations', []),
            'cached': False
        }
        
        # Cache for 30 minutes (chat responses change more frequently)
        response_cache.set(cache_key, result, CACHE_TTL['chat'])
        print(f"[CACHE SET] Chat: {ticker} (TTL: {CACHE_TTL['chat']}s)")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/templates', methods=['GET'])
def get_templates():
    """List available research templates"""
    templates = {
        key: {'name': value['name'], 'step': key}
        for key, value in prompt_templates.items()
    }
    return jsonify({'templates': templates})

@app.route('/api/stock/price/<ticker>', methods=['GET'])
@track_performance('/api/stock/price')
def get_stock_price(ticker):
    """
    Get real-time stock price for a ticker
    Security: Input validation, rate limiting via caching
    """
    try:
        # Security: Validate ticker
        if not ticker or not ticker.isalnum() or len(ticker) > 5:
            return jsonify({'error': 'Invalid ticker format'}), 400
        
        ticker = ticker.upper()
        
        # Check cache first (cache for 1 minute)
        cache_key = f"price:{ticker}"
        cached_price = response_cache.get(cache_key)
        if cached_price:
            cached_price['cached'] = True
            return jsonify(cached_price)
        
        # Fetch real-time price
        price_data = stock_price_service.get_stock_price(ticker)
        
        if not price_data:
            return jsonify({'error': 'Could not fetch price data'}), 404
        
        # Cache for 1 minute
        response_cache.set(cache_key, price_data, 60)
        price_data['cached'] = False
        
        return jsonify(price_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['POST'])
def track_analytics():
    """Track analytics event"""
    try:
        event_data = request.json
        analytics_service.track_event(event_data)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """Get analytics statistics"""
    try:
        date = request.args.get('date')
        stats = analytics_service.get_stats(date)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/popular-stocks', methods=['GET'])
def get_popular_stocks():
    """Get most analyzed stocks"""
    try:
        date = request.args.get('date')
        limit = int(request.args.get('limit', 10))
        stocks = analytics_service.get_popular_stocks(date, limit)
        return jsonify({'stocks': stocks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        # Cleanup expired entries first
        expired = response_cache.cleanup_expired()
        
        return jsonify({
            'size': response_cache.size(),
            'ttl_seconds': response_cache.ttl,
            'expired_cleaned': expired
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cache (admin only - add auth if needed)"""
    try:
        response_cache.clear()
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/compare', methods=['POST'])
@track_performance('/api/research/compare')
def compare_stocks():
    """Compare multiple stocks side-by-side"""
    try:
        data = request.json
        tickers = data.get('tickers', [])
        
        if not tickers or len(tickers) < 2:
            return jsonify({'error': 'At least 2 tickers required'}), 400
        
        if len(tickers) > 3:
            return jsonify({'error': 'Maximum 3 stocks can be compared'}), 400
        
        # Validate tickers
        tickers = [t.upper().strip() for t in tickers if t.strip()]
        
        # Create cache key (sorted tickers for consistent caching)
        sorted_tickers = sorted(tickers)
        cache_key = f"compare:{':'.join(sorted_tickers)}"
        
        # Check cache first
        cached_result = response_cache.get(cache_key)
        if cached_result:
            cached_result['cached'] = True
            return jsonify(cached_result)
        
        # Build comparison prompt
        ticker_list = ', '.join(tickers)
        prompt = f"""Compare these stocks for investment: {ticker_list}

For each stock, provide:
1. Current recommendation (Buy/Hold/Sell)
2. Risk level (Low/Medium/High)
3. Growth potential (Low/Medium/High)
4. 3 key highlights

Then provide:
- A brief comparison summary
- Which stock is the best choice and why

Format your response as JSON with this structure:
{{
  "summary": "brief comparison overview",
  "stocks": [
    {{
      "ticker": "TICKER",
      "recommendation": "Buy/Hold/Sell",
      "risk": "Low/Medium/High",
      "growth": "Low/Medium/High",
      "highlights": ["point 1", "point 2", "point 3"]
    }}
  ],
  "winner": "explanation of best choice"
}}"""
        
        # Call Perplexity API
        response = perplexity_service.query(prompt)
        
        # Try to parse JSON response
        import json
        import re
        
        content = response['content']
        
        # Remove markdown code blocks if present
        if '```json' in content:
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
        elif '```' in content:
            content = re.sub(r'```\s*', '', content)
        
        try:
            result = json.loads(content.strip())
            
            # Ensure all required fields exist
            if 'stocks' not in result:
                raise ValueError('Missing stocks field')
            if 'summary' not in result:
                result['summary'] = 'Stock comparison analysis'
            if 'winner' not in result:
                result['winner'] = 'See analysis above'
                
        except Exception as e:
            # If parsing fails, create structured response from raw content
            result = {
                'summary': content[:500] if len(content) > 500 else content,
                'stocks': [
                    {
                        'ticker': t, 
                        'recommendation': 'Hold', 
                        'risk': 'Medium', 
                        'growth': 'Medium', 
                        'highlights': ['See detailed analysis in summary']
                    } for t in tickers
                ],
                'winner': 'Analysis provided in summary section'
            }
        
        # Add cached flag and cache the result
        result['cached'] = False
        response_cache.set(cache_key, result)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    debug_mode = os.getenv('NODE_ENV') == 'development'
    
    # Production settings
    if not debug_mode:
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(debug=True, port=port)
