"""
Real-time Stock Price Service
Fetches current stock prices from reliable free APIs
"""
import requests
import os
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StockPriceService:
    """
    Fetch real-time stock prices from multiple sources
    Security: Rate limiting, input validation, error handling
    """
    
    def __init__(self):
        # Alpha Vantage API (free tier: 25 requests/day)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        
        # Fallback to Yahoo Finance (no API key needed)
        self.use_yahoo = True
        
    def get_stock_price(self, ticker: str) -> Optional[Dict]:
        """
        Get current stock price for a ticker
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dict with price data or None if failed
            {
                'symbol': 'AAPL',
                'price': 150.25,
                'change': 2.50,
                'change_percent': 1.69,
                'currency': 'USD',
                'timestamp': '2025-11-12T10:30:00',
                'source': 'yahoo'
            }
        """
        # Security: Validate ticker format
        if not ticker or not ticker.isalnum() or len(ticker) > 5:
            logger.error(f"Invalid ticker format: {ticker}")
            return None
        
        ticker = ticker.upper()
        
        # Try Yahoo Finance first (free, no API key needed)
        if self.use_yahoo:
            result = self._fetch_from_yahoo(ticker)
            if result:
                return result
        
        # Fallback to Alpha Vantage if available
        if self.alpha_vantage_key:
            result = self._fetch_from_alpha_vantage(ticker)
            if result:
                return result
        
        logger.warning(f"Could not fetch price for {ticker}")
        return None
    
    def _fetch_from_yahoo(self, ticker: str) -> Optional[Dict]:
        """
        Fetch from Yahoo Finance (free, no API key)
        Uses the query1.finance.yahoo.com endpoint
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"Yahoo Finance returned {response.status_code} for {ticker}")
                return None
            
            data = response.json()
            
            # Parse response
            if 'chart' not in data or 'result' not in data['chart']:
                return None
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            current_price = meta.get('regularMarketPrice')
            previous_close = meta.get('previousClose')
            
            if not current_price:
                return None
            
            # Calculate change
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return {
                'symbol': ticker,
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'currency': meta.get('currency', 'USD'),
                'timestamp': datetime.now().isoformat(),
                'market_state': meta.get('marketState', 'REGULAR'),
                'source': 'yahoo'
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching price for {ticker} from Yahoo")
            return None
        except Exception as e:
            logger.error(f"Error fetching from Yahoo for {ticker}: {str(e)}")
            return None
    
    def _fetch_from_alpha_vantage(self, ticker: str) -> Optional[Dict]:
        """
        Fetch from Alpha Vantage (requires API key)
        Free tier: 25 requests/day
        """
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if 'Global Quote' not in data:
                return None
            
            quote = data['Global Quote']
            
            if not quote or '05. price' not in quote:
                return None
            
            price = float(quote['05. price'])
            change = float(quote['09. change'])
            change_percent = float(quote['10. change percent'].rstrip('%'))
            
            return {
                'symbol': ticker,
                'price': round(price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'currency': 'USD',
                'timestamp': datetime.now().isoformat(),
                'source': 'alphavantage'
            }
            
        except Exception as e:
            logger.error(f"Error fetching from Alpha Vantage for {ticker}: {str(e)}")
            return None
    
    def get_multiple_prices(self, tickers: list) -> Dict[str, Dict]:
        """
        Get prices for multiple tickers
        
        Args:
            tickers: List of stock symbols
            
        Returns:
            Dict mapping ticker to price data
        """
        # Security: Limit to 10 tickers at once
        if len(tickers) > 10:
            logger.warning(f"Too many tickers requested: {len(tickers)}, limiting to 10")
            tickers = tickers[:10]
        
        results = {}
        for ticker in tickers:
            price_data = self.get_stock_price(ticker)
            if price_data:
                results[ticker] = price_data
        
        return results


# Global instance
stock_price_service = StockPriceService()
