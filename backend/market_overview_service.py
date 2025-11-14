"""
Market Overview Service
Fetches market indices, top movers, and sector performance
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MarketOverviewService:
    """Fetch market overview data"""
    
    def get_market_overview(self) -> Optional[Dict]:
        """
        Get comprehensive market overview
        
        Returns:
            Dict with indices, movers, and sectors
        """
        try:
            indices = self._get_major_indices()
            movers = self._get_top_movers()
            sectors = self._get_sector_performance()
            
            return {
                'indices': indices,
                'movers': movers,
                'sectors': sectors
            }
            
        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            return None
    
    def _get_major_indices(self):
        """Get major market indices (S&P 500, NASDAQ, DOW)"""
        indices_symbols = [
            ('^GSPC', 'S&P 500'),
            ('^IXIC', 'NASDAQ'),
            ('^DJI', 'Dow Jones')
        ]
        
        indices = []
        
        for symbol, name in indices_symbols:
            # Try primary endpoint
            index_data = self._fetch_index_data(symbol, name)
            if index_data:
                indices.append(index_data)
                continue
            
            # Try alternative endpoint
            index_data = self._fetch_index_data_alt(symbol, name)
            if index_data:
                indices.append(index_data)
                continue
            
            logger.warning(f"Could not fetch data for {symbol} from any source")
        
        # Use fallback if no indices were fetched
        if len(indices) == 0:
            indices = self._get_fallback_indices()
        
        return indices
    
    def _fetch_index_data(self, symbol: str, name: str) -> Optional[Dict]:
        """Fetch index data from Yahoo Finance chart API"""
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'interval': '1d', 'range': '1d'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                current_price = meta.get('regularMarketPrice')
                previous_close = meta.get('previousClose')
                
                if current_price and previous_close:
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100)
                    
                    return {
                        'symbol': symbol,
                        'name': name,
                        'price': round(current_price, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2)
                    }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from chart API: {str(e)}")
        
        return None
    
    def _fetch_index_data_alt(self, symbol: str, name: str) -> Optional[Dict]:
        """Fetch index data from Yahoo Finance quote API (alternative)"""
        try:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote"
            params = {'symbols': symbol}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'quoteResponse' in data and 'result' in data['quoteResponse']:
                    results = data['quoteResponse']['result']
                    if results and len(results) > 0:
                        quote = results[0]
                        current_price = quote.get('regularMarketPrice')
                        previous_close = quote.get('regularMarketPreviousClose')
                        
                        if current_price and previous_close:
                            change = current_price - previous_close
                            change_percent = (change / previous_close * 100)
                            
                            return {
                                'symbol': symbol,
                                'name': name,
                                'price': round(current_price, 2),
                                'change': round(change, 2),
                                'change_percent': round(change_percent, 2)
                            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from quote API: {str(e)}")
        
        return None
    
    def _get_fallback_indices(self):
        """Get fallback indices data"""
        # Fallback: If no indices fetched, return recent data with note
        if True:
            logger.warning("No indices fetched, using recent market data")
            from datetime import datetime
            indices = [
                {
                    'symbol': '^GSPC', 
                    'name': 'S&P 500', 
                    'price': 5916.98, 
                    'change': 22.44, 
                    'change_percent': 0.38,
                    'note': 'Recent data - Live feed temporarily unavailable'
                },
                {
                    'symbol': '^IXIC', 
                    'name': 'NASDAQ', 
                    'price': 18987.47, 
                    'change': 63.97, 
                    'change_percent': 0.34,
                    'note': 'Recent data - Live feed temporarily unavailable'
                },
                {
                    'symbol': '^DJI', 
                    'name': 'Dow Jones', 
                    'price': 43958.19, 
                    'change': 259.65, 
                    'change_percent': 0.59,
                    'note': 'Recent data - Live feed temporarily unavailable'
                }
            ]
        
        return indices
    
    def _get_top_movers(self):
        """Get top gainers and losers"""
        movers = {
            'gainers': [],
            'losers': []
        }
        
        # Popular stocks to check for movers
        popular_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD', 
            'NFLX', 'DIS', 'BA', 'INTC', 'PYPL', 'COIN', 'UBER', 'ABNB',
            'SHOP', 'SQ', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'TWLO'
        ]
        
        try:
            # Fetch real-time data for popular stocks
            all_stocks = []
            
            for ticker in popular_tickers:
                try:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                    params = {'interval': '1d', 'range': '1d'}
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(url, params=params, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        current_price = meta.get('regularMarketPrice')
                        previous_close = meta.get('previousClose')
                        long_name = meta.get('longName', ticker)
                        
                        if current_price and previous_close:
                            change_percent = ((current_price - previous_close) / previous_close * 100)
                            
                            all_stocks.append({
                                'ticker': ticker,
                                'name': long_name,
                                'price': current_price,
                                'change_percent': change_percent
                            })
                except Exception as e:
                    logger.debug(f"Error fetching {ticker}: {str(e)}")
                    continue
            
            # Sort and get top 5 gainers and losers
            if all_stocks:
                all_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
                movers['gainers'] = all_stocks[:5]
                movers['losers'] = all_stocks[-5:][::-1]  # Reverse to show worst first
            
        except Exception as e:
            logger.error(f"Error fetching movers: {str(e)}")
        
        return movers
    
    def _get_sector_performance(self):
        """Get sector performance"""
        # Sector ETFs as proxies
        sectors = [
            ('XLK', 'Technology'),
            ('XLF', 'Financials'),
            ('XLV', 'Healthcare'),
            ('XLE', 'Energy'),
            ('XLI', 'Industrials'),
            ('XLY', 'Consumer Discretionary'),
            ('XLP', 'Consumer Staples'),
            ('XLB', 'Materials'),
            ('XLRE', 'Real Estate'),
            ('XLU', 'Utilities')
        ]
        
        sector_data = []
        
        for symbol, name in sectors:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {'interval': '1d', 'range': '1d'}
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose')
                    
                    if current_price and previous_close:
                        change_percent = ((current_price - previous_close) / previous_close * 100)
                        
                        sector_data.append({
                            'name': name,
                            'symbol': symbol,
                            'change_percent': round(change_percent, 2)
                        })
                        
            except Exception as e:
                logger.error(f"Error fetching sector {symbol}: {str(e)}")
                continue
        
        return sector_data


# Global instance
market_overview_service = MarketOverviewService()
