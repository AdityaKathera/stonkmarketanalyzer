"""
Stock Chart Data Service
Fetches historical price data for charting
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ChartService:
    """Fetch historical stock data for charts"""
    
    def get_chart_data(self, ticker: str, timeframe: str = '1M') -> Optional[Dict]:
        """
        Get historical price data for charting
        
        Args:
            ticker: Stock symbol
            timeframe: '1D', '1W', '1M', '3M', '1Y', '5Y'
            
        Returns:
            Dict with prices and volumes for charting
        """
        # Validate ticker
        if not ticker or len(ticker) > 15:
            return None
        
        ticker = ticker.upper()
        
        # Map timeframe to Yahoo Finance parameters
        timeframe_map = {
            '1D': ('1d', '5m'),
            '1W': ('5d', '15m'),
            '1M': ('1mo', '1d'),
            '3M': ('3mo', '1d'),
            '1Y': ('1y', '1d'),
            '5Y': ('5y', '1wk')
        }
        
        if timeframe not in timeframe_map:
            timeframe = '1M'
        
        range_param, interval = timeframe_map[timeframe]
        
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'range': range_param,
                'interval': interval
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Yahoo Finance returned {response.status_code} for {ticker}")
                return None
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                return None
            
            result = data['chart']['result'][0]
            
            # Extract timestamps and quotes
            timestamps = result.get('timestamp', [])
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            
            opens = quotes.get('open', [])
            highs = quotes.get('high', [])
            lows = quotes.get('low', [])
            closes = quotes.get('close', [])
            volumes = quotes.get('volume', [])
            
            # Format data for lightweight-charts
            prices = []
            volume_data = []
            
            for i in range(len(timestamps)):
                # Skip if any required value is None
                if (opens[i] is None or highs[i] is None or 
                    lows[i] is None or closes[i] is None):
                    continue
                
                prices.append({
                    'time': timestamps[i],
                    'open': round(opens[i], 2),
                    'high': round(highs[i], 2),
                    'low': round(lows[i], 2),
                    'close': round(closes[i], 2)
                })
                
                if volumes[i] is not None:
                    volume_data.append({
                        'time': timestamps[i],
                        'value': volumes[i],
                        'color': '#26a69a' if closes[i] >= opens[i] else '#ef5350'
                    })
            
            return {
                'ticker': ticker,
                'timeframe': timeframe,
                'prices': prices,
                'volumes': volume_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching chart data for {ticker}: {str(e)}")
            return None


# Global instance
chart_service = ChartService()
