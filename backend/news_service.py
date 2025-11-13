"""
News Service - Fetch latest news for stocks
Uses Alpha Vantage News API (free tier)
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class NewsService:
    def __init__(self):
        # Alpha Vantage provides free news API
        self.base_url = "https://www.alphavantage.co/query"
        # Using demo key for now - can be upgraded
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        
        # Cache: {ticker: {'news': [...], 'timestamp': datetime}}
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def get_news_for_stock(self, ticker: str, limit: int = 5) -> List[Dict]:
        """
        Get latest news for a specific stock ticker
        Returns list of news articles with title, url, source, time_published, summary
        """
        # Check cache first
        if ticker in self.cache:
            cached_data = self.cache[ticker]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                print(f"[NewsService] Cache hit for {ticker}")
                return cached_data['news'][:limit]
        
        print(f"[NewsService] Fetching news for {ticker}")
        
        try:
            # Alpha Vantage News & Sentiments API
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': self.api_key,
                'limit': limit * 2  # Fetch more to filter
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data or 'Note' in data:
                print(f"[NewsService] API Error: {data}")
                return self._get_fallback_news(ticker, limit)
            
            # Parse news feed
            news_items = []
            feed = data.get('feed', [])
            
            print(f"[NewsService] Found {len(feed)} news items for {ticker}")
            
            for item in feed[:limit]:
                news_items.append({
                    'title': item.get('title', 'No title'),
                    'url': item.get('url', ''),
                    'source': item.get('source', 'Unknown'),
                    'time_published': item.get('time_published', ''),
                    'summary': item.get('summary', ''),
                    'banner_image': item.get('banner_image'),
                    'sentiment_score': item.get('overall_sentiment_score', 0),
                    'sentiment_label': item.get('overall_sentiment_label', 'Neutral')
                })
            
            # If no news found, use fallback
            if not news_items:
                print(f"[NewsService] No news found for {ticker}, using fallback")
                news_items = self._get_fallback_news(ticker, limit)
            
            # Cache the results
            self.cache[ticker] = {
                'news': news_items,
                'timestamp': datetime.now()
            }
            
            return news_items
            
        except Exception as e:
            print(f"[NewsService] Error fetching news for {ticker}: {e}")
            return self._get_fallback_news(ticker, limit)
    
    def get_news_for_watchlist(self, tickers: List[str], limit_per_stock: int = 3) -> Dict[str, List[Dict]]:
        """
        Get news for multiple stocks in watchlist
        Returns dict: {ticker: [news_items]}
        """
        results = {}
        
        for ticker in tickers:
            results[ticker] = self.get_news_for_stock(ticker, limit_per_stock)
            # Rate limiting - Alpha Vantage free tier: 5 calls/min
            time.sleep(0.5)
        
        return results
    
    def _get_fallback_news(self, ticker: str, limit: int) -> List[Dict]:
        """
        Fallback news when API fails or rate limited
        Provides multiple helpful links for the stock
        """
        current_time = datetime.now().strftime('%Y%m%dT%H%M%S')
        
        return [
            {
                'title': f'📊 {ticker} Real-Time Market Data & Analysis',
                'url': f'https://finance.yahoo.com/quote/{ticker}',
                'source': 'Yahoo Finance',
                'time_published': current_time,
                'summary': f'Access comprehensive real-time data for {ticker} including live price quotes, interactive charts, historical performance, and detailed financial statements.',
                'banner_image': None,
                'sentiment_score': 0,
                'sentiment_label': 'Neutral'
            },
            {
                'title': f'📰 Latest {ticker} News & Market Updates',
                'url': f'https://www.google.com/finance/quote/{ticker}:NYSE',
                'source': 'Google Finance',
                'time_published': current_time,
                'summary': f'Stay informed with the latest breaking news, earnings reports, analyst ratings, and market-moving events for {ticker}.',
                'banner_image': None,
                'sentiment_score': 0,
                'sentiment_label': 'Neutral'
            },
            {
                'title': f'💼 {ticker} Company Profile & Financial Health',
                'url': f'https://www.marketwatch.com/investing/stock/{ticker.lower()}',
                'source': 'MarketWatch',
                'time_published': current_time,
                'summary': f'Explore detailed company fundamentals, quarterly earnings, balance sheets, and expert analysis for {ticker}.',
                'banner_image': None,
                'sentiment_score': 0,
                'sentiment_label': 'Neutral'
            }
        ][:limit]
    
    def clear_cache(self):
        """Clear all cached news"""
        self.cache = {}
        print("[NewsService] Cache cleared")

# Singleton instance
_news_service = None

def get_news_service() -> NewsService:
    """Get or create NewsService singleton"""
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service
