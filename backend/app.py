from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import hashlib

from services.perplexity_service import PerplexityService
from prompts.templates import prompt_templates, free_chat_template
from analytics import AnalyticsService
from secure_portal import setup_portal_routes
from cache import SimpleCache

load_dotenv()

app = Flask(__name__)

# Configure CORS with environment-based origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=allowed_origins)

perplexity_service = PerplexityService(os.getenv('PERPLEXITY_API_KEY'))
analytics_service = AnalyticsService()

# Initialize cache with 1 hour TTL
response_cache = SimpleCache(ttl_seconds=3600)

# Setup secure admin portal
portal_path, portal_username = setup_portal_routes(app, analytics_service)
print(f"🔒 Secure portal initialized at: /api/{portal_path}")
print(f"🔑 Portal username: {portal_username}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Stock Research API is running'})

@app.route('/api/research/guided', methods=['POST'])
def guided_research():
    """Execute a guided research step"""
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
        
        # Get the prompt template and inject user inputs
        template_func = prompt_templates[step]['template']
        prompt = template_func(ticker, horizon, risk_level)
        
        print(f"[DEBUG] Calling Perplexity API...")
        
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
        
        return jsonify(result)
    
    except Exception as e:
        print(f"[ERROR] Guided research failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/chat', methods=['POST'])
def free_chat():
    """Handle free-form chat queries"""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper()
        question = data.get('question', '')
        
        if not ticker or not question:
            return jsonify({'error': 'Ticker and question are required'}), 400
        
        # Generate prompt for free chat
        prompt = free_chat_template(ticker, question)
        
        # Call Perplexity API
        response = perplexity_service.query(prompt)
        
        return jsonify({
            'ticker': ticker,
            'question': question,
            'response': response['content'],
            'citations': response.get('citations', [])
        })
    
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
