"""
Portfolio Service - Enhanced portfolio management with real-time prices and analytics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any
from services.stock_price_service import stock_price_service

DB_PATH = 'users.db'

class PortfolioService:
    """Service for portfolio management and analytics"""
    
    def __init__(self):
        self.price_cache = {}  # Cache prices for 1 minute
        self.cache_expiry = {}
    
    def get_current_price(self, ticker: str) -> float:
        """Get current stock price with caching"""
        now = datetime.now()
        
        # Check cache
        if ticker in self.price_cache:
            if ticker in self.cache_expiry and now < self.cache_expiry[ticker]:
                return self.price_cache[ticker]
        
        # Fetch new price
        try:
            price_data = stock_price_service.get_stock_price(ticker)
            if price_data and 'price' in price_data:
                price = price_data['price']
                self.price_cache[ticker] = price
                self.cache_expiry[ticker] = now + timedelta(minutes=1)
                return price
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
        
        return None
    
    def calculate_holding_metrics(self, holding: Dict) -> Dict:
        """Calculate metrics for a single holding"""
        ticker = holding['ticker']
        shares = float(holding['shares'])
        purchase_price = float(holding['purchase_price'])
        
        # Get current price
        current_price = self.get_current_price(ticker)
        
        if current_price is None:
            # If we can't get current price, return basic info
            return {
                **holding,
                'current_price': None,
                'current_value': None,
                'cost_basis': shares * purchase_price,
                'unrealized_gain': None,
                'return_percentage': None,
                'return_dollar': None
            }
        
        # Calculate metrics
        cost_basis = shares * purchase_price
        current_value = shares * current_price
        unrealized_gain = current_value - cost_basis
        return_percentage = (unrealized_gain / cost_basis) * 100 if cost_basis > 0 else 0
        
        return {
            **holding,
            'current_price': round(current_price, 2),
            'current_value': round(current_value, 2),
            'cost_basis': round(cost_basis, 2),
            'unrealized_gain': round(unrealized_gain, 2),
            'return_percentage': round(return_percentage, 2),
            'return_dollar': round(unrealized_gain, 2),
            'day_change': None,  # TODO: Add day change calculation
            'day_change_percent': None
        }
    
    def get_portfolio_with_metrics(self, user_id: int) -> Dict[str, Any]:
        """Get portfolio with real-time prices and metrics"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all holdings
        cursor.execute('''
            SELECT id, user_id, ticker, shares, purchase_price, purchase_date, notes, created_at
            FROM portfolio
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        holdings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not holdings:
            return {
                'holdings': [],
                'summary': {
                    'total_value': 0,
                    'total_cost': 0,
                    'total_gain': 0,
                    'total_return_percentage': 0,
                    'holdings_count': 0,
                    'best_performer': None,
                    'worst_performer': None
                }
            }
        
        # Calculate metrics for each holding
        enriched_holdings = []
        for holding in holdings:
            enriched = self.calculate_holding_metrics(holding)
            enriched_holdings.append(enriched)
        
        # Calculate portfolio summary
        summary = self.calculate_portfolio_summary(enriched_holdings)
        
        return {
            'holdings': enriched_holdings,
            'summary': summary
        }
    
    def calculate_portfolio_summary(self, holdings: List[Dict]) -> Dict:
        """Calculate portfolio-level summary metrics"""
        if not holdings:
            return {
                'total_value': 0,
                'total_cost': 0,
                'total_gain': 0,
                'total_return_percentage': 0,
                'holdings_count': 0,
                'best_performer': None,
                'worst_performer': None
            }
        
        # Filter out holdings without current prices
        valid_holdings = [h for h in holdings if h['current_value'] is not None]
        
        if not valid_holdings:
            # If no valid prices, return cost basis only
            total_cost = sum(h['cost_basis'] for h in holdings)
            return {
                'total_value': None,
                'total_cost': round(total_cost, 2),
                'total_gain': None,
                'total_return_percentage': None,
                'holdings_count': len(holdings),
                'best_performer': None,
                'worst_performer': None
            }
        
        # Calculate totals
        total_value = sum(h['current_value'] for h in valid_holdings)
        total_cost = sum(h['cost_basis'] for h in valid_holdings)
        total_gain = total_value - total_cost
        total_return_percentage = (total_gain / total_cost) * 100 if total_cost > 0 else 0
        
        # Find best and worst performers
        sorted_by_return = sorted(
            [h for h in valid_holdings if h['return_percentage'] is not None],
            key=lambda x: x['return_percentage'],
            reverse=True
        )
        
        best_performer = None
        worst_performer = None
        
        if sorted_by_return:
            best = sorted_by_return[0]
            worst = sorted_by_return[-1]
            
            best_performer = {
                'ticker': best['ticker'],
                'return_percentage': best['return_percentage'],
                'return_dollar': best['return_dollar']
            }
            
            worst_performer = {
                'ticker': worst['ticker'],
                'return_percentage': worst['return_percentage'],
                'return_dollar': worst['return_dollar']
            }
        
        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_gain': round(total_gain, 2),
            'total_return_percentage': round(total_return_percentage, 2),
            'holdings_count': len(holdings),
            'valid_holdings_count': len(valid_holdings),
            'best_performer': best_performer,
            'worst_performer': worst_performer,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_portfolio_allocation(self, user_id: int) -> Dict:
        """Get portfolio allocation by stock"""
        portfolio_data = self.get_portfolio_with_metrics(user_id)
        holdings = portfolio_data['holdings']
        
        if not holdings:
            return {'allocation': []}
        
        # Filter valid holdings
        valid_holdings = [h for h in holdings if h['current_value'] is not None]
        
        if not valid_holdings:
            return {'allocation': []}
        
        total_value = sum(h['current_value'] for h in valid_holdings)
        
        allocation = []
        for holding in valid_holdings:
            percentage = (holding['current_value'] / total_value) * 100 if total_value > 0 else 0
            allocation.append({
                'ticker': holding['ticker'],
                'value': holding['current_value'],
                'percentage': round(percentage, 2),
                'shares': holding['shares']
            })
        
        # Sort by percentage descending
        allocation.sort(key=lambda x: x['percentage'], reverse=True)
        
        return {'allocation': allocation}

# Global instance
portfolio_service = PortfolioService()
