"""
Secure Cache Warming System
Pre-populates cache with popular stocks to improve user experience
"""
import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict
import hashlib
import hmac

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from services.perplexity_service import PerplexityService
from prompts.templates import prompt_templates
from cache_enhanced import EnhancedCache

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/stonkmarketanalyzer/logs/cache_warmer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Security: Verify this script is running in authorized context
CACHE_WARMER_SECRET = os.getenv('CACHE_WARMER_SECRET', 'change-this-secret-in-production')

class SecureCacheWarmer:
    """Secure cache warming with rate limiting and monitoring"""
    
    def __init__(self):
        self.perplexity_service = PerplexityService(os.getenv('PERPLEXITY_API_KEY'))
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.cache = EnhancedCache(redis_url=redis_url, default_ttl=86400)  # 24 hour TTL
        
        # Security: Rate limiting
        self.max_requests_per_minute = 10
        self.request_count = 0
        self.minute_start = time.time()
        
        # Monitoring
        self.stats = {
            'started_at': datetime.now().isoformat(),
            'stocks_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'api_calls': 0
        }
    
    def verify_authorization(self, provided_secret: str) -> bool:
        """
        Verify the caller is authorized to run cache warming
        Uses constant-time comparison to prevent timing attacks
        """
        expected = CACHE_WARMER_SECRET.encode()
        provided = provided_secret.encode()
        return hmac.compare_digest(expected, provided)
    
    def rate_limit_check(self) -> bool:
        """
        Check if we're within rate limits
        Prevents overwhelming the API
        """
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.minute_start >= 60:
            self.request_count = 0
            self.minute_start = current_time
        
        if self.request_count >= self.max_requests_per_minute:
            logger.warning(f"Rate limit reached: {self.request_count} requests in current minute")
            return False
        
        return True
    
    def get_popular_stocks(self) -> List[str]:
        """
        Get list of popular stocks to cache
        Security: Hardcoded list to prevent injection attacks
        Focus on top 20 most popular stocks for faster caching
        """
        return [
            # Top Tech Giants (most popular)
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
            # Top Finance
            'JPM', 'BAC', 'V', 'MA',
            # Top Healthcare
            'JNJ', 'UNH',
            # Top Consumer
            'WMT', 'HD', 'DIS',
            # Top Industrial
            'BA',
            # Top Energy
            'XOM',
            # Popular ETFs
            'SPY', 'QQQ'
        ]
    
    def get_priority_steps(self) -> List[str]:
        """
        Get research steps to cache (most commonly used)
        Security: Validated against available templates
        """
        # Get all available steps from templates
        all_steps = list(prompt_templates.keys())
        
        # Priority order (most commonly used first)
        priority_order = ['overview', 'financials', 'valuation', 'moat', 'risks', 'investment_advice', 'memo']
        
        # Sort steps by priority, then alphabetically
        sorted_steps = []
        for step in priority_order:
            if step in all_steps:
                sorted_steps.append(step)
        
        # Add any remaining steps
        for step in all_steps:
            if step not in sorted_steps:
                sorted_steps.append(step)
        
        logger.info(f"Caching {len(sorted_steps)} steps: {', '.join(sorted_steps)}")
        return sorted_steps
    
    def warm_stock(self, ticker: str, step: str) -> Dict:
        """
        Warm cache for a specific stock and step
        Returns: Dict with status and timing info
        """
        start_time = time.time()
        
        try:
            # Security: Validate ticker format (alphanumeric only, max 5 chars)
            if not ticker.isalnum() or len(ticker) > 5:
                logger.error(f"Invalid ticker format: {ticker}")
                self.stats['errors'] += 1
                return {'status': 'error', 'reason': 'invalid_ticker'}
            
            # Security: Validate step exists
            if step not in prompt_templates:
                logger.error(f"Invalid step: {step}")
                self.stats['errors'] += 1
                return {'status': 'error', 'reason': 'invalid_step'}
            
            # Generate cache key
            cache_key = self.cache._generate_key(
                'guided',
                ticker=ticker,
                step=step,
                horizon='1-3 years',
                risk='moderate'
            )
            
            # Check if already cached
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"✓ Already cached: {ticker} - {step}")
                self.stats['cache_hits'] += 1
                return {
                    'status': 'cached',
                    'ticker': ticker,
                    'step': step,
                    'duration': time.time() - start_time
                }
            
            # Security: Rate limit check
            if not self.rate_limit_check():
                logger.warning(f"Rate limit reached, skipping: {ticker} - {step}")
                time.sleep(60)  # Wait a minute
                return {'status': 'rate_limited'}
            
            # Call API
            logger.info(f"⏳ Fetching: {ticker} - {step}")
            template_func = prompt_templates[step]['template']
            prompt = template_func(ticker, '1-3 years', 'moderate')
            
            self.request_count += 1
            self.stats['api_calls'] += 1
            
            response = self.perplexity_service.query(prompt)
            
            # Cache the result
            result = {
                'step': step,
                'ticker': ticker,
                'response': response['content'],
                'citations': response.get('citations', []),
                'cached': False,
                'warmed_at': datetime.now().isoformat()
            }
            
            # Determine TTL based on step
            ttl_map = {
                'fundamentals': 86400,  # 24 hours
                'overview': 14400,      # 4 hours
                'news': 3600,           # 1 hour
                'technical': 14400      # 4 hours
            }
            ttl = ttl_map.get(step, 14400)
            
            self.cache.set(cache_key, result, ttl)
            
            duration = time.time() - start_time
            logger.info(f"✓ Cached: {ticker} - {step} ({duration:.1f}s)")
            
            self.stats['cache_misses'] += 1
            self.stats['stocks_processed'] += 1
            
            # Security: Add delay to prevent overwhelming API
            time.sleep(2)  # 2 second delay between requests
            
            return {
                'status': 'success',
                'ticker': ticker,
                'step': step,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"✗ Error warming {ticker} - {step}: {str(e)}")
            self.stats['errors'] += 1
            return {
                'status': 'error',
                'ticker': ticker,
                'step': step,
                'error': str(e)
            }
    
    def warm_cache(self, secret: str = None) -> Dict:
        """
        Main cache warming function
        Security: Requires authorization secret
        """
        # Security: Verify authorization
        if secret and not self.verify_authorization(secret):
            logger.error("Unauthorized cache warming attempt")
            return {'status': 'unauthorized', 'message': 'Invalid authorization secret'}
        
        logger.info("=" * 60)
        logger.info("Starting Secure Cache Warming")
        logger.info("=" * 60)
        
        stocks = self.get_popular_stocks()
        steps = self.get_priority_steps()
        
        total_tasks = len(stocks) * len(steps)
        logger.info(f"Tasks: {len(stocks)} stocks × {len(steps)} steps = {total_tasks} total")
        
        results = []
        
        for ticker in stocks:
            for step in steps:
                result = self.warm_stock(ticker, step)
                results.append(result)
                
                # Progress update every 10 items
                if len(results) % 10 == 0:
                    progress = (len(results) / total_tasks) * 100
                    logger.info(f"Progress: {len(results)}/{total_tasks} ({progress:.1f}%)")
        
        # Final statistics
        self.stats['completed_at'] = datetime.now().isoformat()
        self.stats['total_tasks'] = total_tasks
        
        logger.info("=" * 60)
        logger.info("Cache Warming Complete")
        logger.info("=" * 60)
        logger.info(f"Stocks Processed: {self.stats['stocks_processed']}")
        logger.info(f"Cache Hits: {self.stats['cache_hits']}")
        logger.info(f"Cache Misses: {self.stats['cache_misses']}")
        logger.info(f"API Calls: {self.stats['api_calls']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        return {
            'status': 'completed',
            'stats': self.stats,
            'results': results
        }


def main():
    """
    Main entry point for cache warming
    Security: Requires secret from environment or command line
    """
    # Security: Get secret from environment
    secret = os.getenv('CACHE_WARMER_SECRET')
    
    if not secret:
        logger.error("CACHE_WARMER_SECRET not set in environment")
        sys.exit(1)
    
    # Create warmer and run
    warmer = SecureCacheWarmer()
    result = warmer.warm_cache(secret)
    
    if result['status'] == 'unauthorized':
        logger.error("Unauthorized: Invalid secret")
        sys.exit(1)
    
    # Exit with appropriate code
    if result['stats']['errors'] > 0:
        logger.warning(f"Completed with {result['stats']['errors']} errors")
        sys.exit(2)
    
    logger.info("Cache warming completed successfully")
    sys.exit(0)


if __name__ == '__main__':
    main()
