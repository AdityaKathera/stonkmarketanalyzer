"""
Market Overview Service - Multi-Country Support
Fetches market indices, top movers, and sector performance for multiple countries
"""
import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class MarketOverviewService:
    """Fetch market overview data with multi-country support and caching"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Country configurations
        self.countries = {
            'US': {
                'name': 'United States',
                'indices': [
                    ('^GSPC', 'S&P 500'),
                    ('^IXIC', 'NASDAQ'),
                    ('^DJI', 'Dow Jones')
                ],
                'popular_stocks': [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AMD',
                    'NFLX', 'DIS', 'BA', 'INTC', 'PYPL', 'COIN', 'UBER', 'ABNB',
                    'SHOP', 'SQ', 'SNAP', 'PINS', 'ROKU', 'ZM', 'DOCU', 'TWLO',
                    'CRM', 'ORCL', 'CSCO', 'ADBE', 'QCOM', 'TXN'
                ],
                'sectors': [
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
            },
            'IN': {
                'name': 'India',
                'indices': [
                    ('^NSEI', 'NIFTY 50'),
                    ('^BSESN', 'SENSEX'),
                    ('^NSEBANK', 'BANK NIFTY')
                ],
                'popular_stocks': [
                    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                    'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                    'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'TITAN.NS',
                    'BAJFINANCE.NS', 'HCLTECH.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS',
                    'ADANIENT.NS', 'TATAMOTORS.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS'
                ],
                'sectors': []
            },
            'UK': {
                'name': 'United Kingdom',
                'indices': [
                    ('^FTSE', 'FTSE 100'),
                    ('^FTMC', 'FTSE 250'),
                    ('^FTAI', 'FTSE All-Share')
                ],
                'popular_stocks': [
                    'SHEL.L', 'AZN.L', 'HSBA.L', 'ULVR.L', 'DGE.L', 'BP.L',
                    'GSK.L', 'RIO.L', 'LSEG.L', 'NG.L', 'BARC.L', 'LLOY.L',
                    'VOD.L', 'PRU.L', 'BT-A.L', 'TSCO.L', 'AAL.L', 'IMB.L',
                    'BATS.L', 'CRH.L', 'REL.L', 'EXPN.L', 'STAN.L', 'GLEN.L'
                ],
                'sectors': []
            }
        }
    
    def get_market_overview(self, country: str = 'US') -> Optional[Dict]:
        """
        Get comprehensive market overview for a specific country
        
        Args:
            country: Country code (US, IN, UK)
            
        Returns:
            Dict with indices, movers, and sectors
        """
        # Check cache first
        cache_key = f"market_overview_{country}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                logger.info(f"Returning cached data for {country}")
                return cached_data
        
        try:
            if country not in self.countries:
                country = 'US'  # Default to US
            
            config = self.countries[country]
            
            indices = self._get_major_indices(config['indices'])
            movers = self._get_top_movers(config['popular_stocks'])
            sectors = self._get_sector_performance(config['sectors']) if config['sectors'] else []
            
            result = {
                'country': country,
                'country_name': config['name'],
                'indices': indices,
                'movers': movers,
                'sectors': sectors,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = (result, time.time())
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching market overview for {country}: {str(e)}")
            return None
    
    def get_available_countries(self) -> List[Dict]:
        """Get list of available countries"""
        return [
            {'code': code, 'name': config['name']}
            for code, config in self.countries.items()
        ]
    
    def _get_major_indices(self, indices_symbols: List[tuple]):
        """Get major market indices"""
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
            
            logger.warning(f"Could not fetch data for {symbol}")
        
        return indices
    
    def _fetch_index_data(self, symbol: str, name: str) -> Optional[Dict]:
        """Fetch index data from Yahoo Finance chart API"""
        try:
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'interval': '1d', 'range': '1d'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://finance.yahoo.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose') or meta.get('chartPreviousClose')
                    
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
            logger.debug(f"Error fetching {symbol} from chart API: {str(e)}")
        
        return None
    
    def _fetch_index_data_alt(self, symbol: str, name: str) -> Optional[Dict]:
        """Fetch index data from Yahoo Finance quote API (alternative) - DISABLED"""
        # This endpoint is returning 401, skip it
        return None
    
    def _get_top_movers(self, popular_tickers: List[str]):
        """Get top gainers and losers"""
        movers = {
            'gainers': [],
            'losers': []
        }
        
        try:
            # Fetch real-time data for popular stocks
            all_stocks = []
            
            # Try batch API first
            batch_size = 10
            for i in range(0, len(popular_tickers), batch_size):
                batch = popular_tickers[i:i+batch_size]
                batch_stocks = self._fetch_batch_quotes(batch)
                all_stocks.extend(batch_stocks)
                time.sleep(0.2)  # Small delay to avoid rate limiting
            
            # If batch API failed, try individual fetching for first 15 stocks
            if len(all_stocks) < 5:
                logger.warning(f"Batch API returned only {len(all_stocks)} stocks, trying individual fetching")
                all_stocks = []
                for ticker in popular_tickers[:15]:  # Limit to 15 to avoid timeout
                    stock_data = self._fetch_single_stock(ticker)
                    if stock_data:
                        all_stocks.append(stock_data)
                    time.sleep(0.1)
            
            # Sort and get top 5 gainers and losers
            if all_stocks and len(all_stocks) >= 5:
                all_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
                movers['gainers'] = all_stocks[:5]
                movers['losers'] = all_stocks[-5:][::-1]  # Reverse to show worst first
                
                logger.info(f"Found {len(all_stocks)} stocks, {len(movers['gainers'])} gainers, {len(movers['losers'])} losers")
            else:
                logger.warning(f"Insufficient movers data: only {len(all_stocks)} stocks fetched")
            
        except Exception as e:
            logger.error(f"Error fetching movers: {str(e)}", exc_info=True)
        
        return movers
    
    def _fetch_batch_quotes(self, tickers: List[str]) -> List[Dict]:
        """Fetch quotes for multiple tickers in one request"""
        stocks = []
        
        # Yahoo Finance batch API is unreliable, use individual fetching instead
        logger.info(f"Fetching {len(tickers)} stocks individually")
        
        for ticker in tickers:
            stock_data = self._fetch_single_stock(ticker)
            if stock_data:
                stocks.append(stock_data)
            time.sleep(0.15)  # Rate limiting
        
        return stocks
    
    def _fetch_single_stock(self, ticker: str) -> Optional[Dict]:
        """Fetch data for a single stock (fallback method)"""
        try:
            # Try chart API first
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {'interval': '1d', 'range': '1d'}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://finance.yahoo.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    current_price = meta.get('regularMarketPrice')
                    previous_close = meta.get('previousClose') or meta.get('chartPreviousClose')
                    long_name = meta.get('longName') or meta.get('shortName') or ticker
                    
                    if current_price and previous_close and current_price > 0 and previous_close > 0:
                        change_percent = ((current_price - previous_close) / previous_close * 100)
                        
                        return {
                            'ticker': ticker,
                            'name': long_name,
                            'price': round(current_price, 2),
                            'change_percent': round(change_percent, 2)
                        }
        except Exception as e:
            logger.debug(f"Error fetching single stock {ticker}: {str(e)}")
        
        return None
    
    def _get_sector_performance(self, sectors: List[tuple]):
        """Get sector performance"""
        sector_data = []
        
        for symbol, name in sectors:
            try:
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {'interval': '1d', 'range': '1d'}
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://finance.yahoo.com/'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        current_price = meta.get('regularMarketPrice')
                        previous_close = meta.get('previousClose') or meta.get('chartPreviousClose')
                        
                        if current_price and previous_close:
                            change_percent = ((current_price - previous_close) / previous_close * 100)
                            
                            sector_data.append({
                                'name': name,
                                'symbol': symbol,
                                'change_percent': round(change_percent, 2)
                            })
                        
            except Exception as e:
                logger.debug(f"Error fetching sector {symbol}: {str(e)}")
                continue
        
        return sector_data


# Global instance
market_overview_service = MarketOverviewService()
