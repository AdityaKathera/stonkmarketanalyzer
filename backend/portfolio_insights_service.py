"""
Portfolio Insights Service
Analyzes user portfolios and generates AI-powered insights
"""

import os
from datetime import datetime, timedelta
from services.perplexity_service import PerplexityService
from services.stock_price_service import StockPriceService
import sqlite3

DB_PATH = 'users.db'

# Simple in-memory cache
insights_cache = {}
CACHE_DURATION = timedelta(hours=1)

class PortfolioInsightsService:
    def __init__(self):
        self.perplexity = PerplexityService(os.getenv('PERPLEXITY_API_KEY'))
        self.stock_service = StockPriceService()
    
    def get_portfolio_insights(self, user_id):
        """Get AI-generated insights for user's portfolio"""
        
        # Check cache
        cache_key = f"insights_{user_id}"
        if cache_key in insights_cache:
            cached_data, cached_time = insights_cache[cache_key]
            if datetime.now() - cached_time < CACHE_DURATION:
                return cached_data
        
        # Get portfolio data
        portfolio = self._get_user_portfolio(user_id)
        
        if not portfolio:
            return {
                'insights': [],
                'summary': {
                    'total_value': 0,
                    'total_holdings': 0,
                    'diversification_score': 0
                }
            }
        
        # Calculate metrics
        metrics = self._calculate_portfolio_metrics(portfolio)
        
        # Generate AI insights
        ai_insights = self._generate_ai_insights(portfolio, metrics)
        
        # Combine all insights
        all_insights = []
        
        # Add diversification insight
        all_insights.append(self._create_diversification_insight(metrics))
        
        # Add risk warnings
        risk_insights = self._identify_risks(metrics)
        all_insights.extend(risk_insights)
        
        # Add AI-generated insights
        all_insights.extend(ai_insights)
        
        # Add performance insight if available
        perf_insight = self._create_performance_insight(metrics)
        if perf_insight:
            all_insights.append(perf_insight)
        
        result = {
            'insights': all_insights,
            'summary': {
                'total_value': metrics['total_value'],
                'total_holdings': metrics['total_holdings'],
                'diversification_score': metrics['diversification_score'],
                'top_holding': metrics.get('top_holding'),
                'sector_count': len(metrics['sectors'])
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # Cache the result
        insights_cache[cache_key] = (result, datetime.now())
        
        return result
    
    def _get_user_portfolio(self, user_id):
        """Fetch user's portfolio from database"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT ticker, shares, purchase_price, purchase_date
            FROM portfolio
            WHERE user_id = ?
            ORDER BY ticker
        ''', (user_id,))
        
        holdings = [dict(row) for row in c.fetchall()]
        conn.close()
        
        # Enrich with current prices
        for holding in holdings:
            try:
                price_data = self.stock_service.get_stock_price(holding['ticker'])
                holding['current_price'] = price_data.get('price', holding['purchase_price'])
                holding['current_value'] = holding['current_price'] * holding['shares']
                holding['gain_loss'] = (holding['current_price'] - holding['purchase_price']) * holding['shares']
                holding['gain_loss_pct'] = ((holding['current_price'] - holding['purchase_price']) / holding['purchase_price']) * 100
            except:
                holding['current_price'] = holding['purchase_price']
                holding['current_value'] = holding['purchase_price'] * holding['shares']
                holding['gain_loss'] = 0
                holding['gain_loss_pct'] = 0
        
        return holdings
    
    def _calculate_portfolio_metrics(self, portfolio):
        """Calculate key portfolio metrics"""
        total_value = sum(h['current_value'] for h in portfolio)
        
        # Calculate sector allocation (simplified - using ticker prefixes)
        sectors = {}
        for holding in portfolio:
            # Simplified sector mapping - in production, use proper API
            sector = self._get_sector(holding['ticker'])
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += holding['current_value']
        
        # Calculate percentages
        for sector in sectors:
            sectors[sector] = (sectors[sector] / total_value) * 100 if total_value > 0 else 0
        
        # Find top holding
        top_holding = max(portfolio, key=lambda x: x['current_value']) if portfolio else None
        top_holding_pct = (top_holding['current_value'] / total_value * 100) if top_holding and total_value > 0 else 0
        
        # Calculate diversification score (0-100)
        # Higher score = better diversification
        num_holdings = len(portfolio)
        num_sectors = len(sectors)
        max_sector_pct = max(sectors.values()) if sectors else 100
        
        diversification_score = 0
        if num_holdings > 0:
            # Factor 1: Number of holdings (max 40 points)
            holdings_score = min(num_holdings * 5, 40)
            
            # Factor 2: Sector diversity (max 30 points)
            sector_score = min(num_sectors * 10, 30)
            
            # Factor 3: Balance (max 30 points) - penalize concentration
            balance_score = max(0, 30 - (max_sector_pct - 20))
            
            diversification_score = int(holdings_score + sector_score + balance_score)
        
        return {
            'total_value': total_value,
            'total_holdings': len(portfolio),
            'sectors': sectors,
            'top_holding': {
                'ticker': top_holding['ticker'],
                'percentage': top_holding_pct,
                'value': top_holding['current_value']
            } if top_holding else None,
            'diversification_score': diversification_score,
            'portfolio': portfolio
        }
    
    def _get_sector(self, ticker):
        """Simplified sector mapping - in production, use proper API"""
        # Tech stocks
        tech = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'META', 'NVDA', 'AMD', 'INTC', 'TSLA', 'AMZN']
        # Finance
        finance = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA']
        # Healthcare
        healthcare = ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'LLY']
        # Consumer
        consumer = ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST']
        
        if ticker in tech:
            return 'Technology'
        elif ticker in finance:
            return 'Finance'
        elif ticker in healthcare:
            return 'Healthcare'
        elif ticker in consumer:
            return 'Consumer'
        else:
            return 'Other'
    
    def _create_diversification_insight(self, metrics):
        """Create diversification insight"""
        score = metrics['diversification_score']
        
        if score >= 80:
            level = 'Excellent'
            icon = '🏆'
            type_class = 'success'
            message = f"Your portfolio is well-diversified across {len(metrics['sectors'])} sectors with {metrics['total_holdings']} holdings."
        elif score >= 60:
            level = 'Good'
            icon = '🎯'
            type_class = 'info'
            message = f"Your portfolio is moderately diversified. Consider adding more sectors for better risk management."
        elif score >= 40:
            level = 'Fair'
            icon = '⚠️'
            type_class = 'warning'
            message = f"Your portfolio has limited diversification. Adding holdings in different sectors would reduce risk."
        else:
            level = 'Poor'
            icon = '⚠️'
            type_class = 'warning'
            message = f"Your portfolio is highly concentrated. Diversification across sectors and holdings is recommended."
        
        return {
            'type': type_class,
            'icon': icon,
            'title': f'Diversification Score: {score}/100 ({level})',
            'message': message,
            'details': f"Holdings: {metrics['total_holdings']} | Sectors: {len(metrics['sectors'])}"
        }
    
    def _identify_risks(self, metrics):
        """Identify portfolio risks"""
        risks = []
        
        # Check for concentration risk
        if metrics['top_holding'] and metrics['top_holding']['percentage'] > 40:
            risks.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': 'High Concentration Risk',
                'message': f"{metrics['top_holding']['ticker']} represents {metrics['top_holding']['percentage']:.1f}% of your portfolio. Consider reducing exposure to below 30%.",
                'details': f"Current: ${metrics['top_holding']['value']:,.2f}"
            })
        
        # Check for sector concentration
        max_sector = max(metrics['sectors'].items(), key=lambda x: x[1]) if metrics['sectors'] else None
        if max_sector and max_sector[1] > 50:
            risks.append({
                'type': 'warning',
                'icon': '📊',
                'title': 'Sector Concentration',
                'message': f"{max_sector[0]} sector represents {max_sector[1]:.1f}% of your portfolio. Diversify into other sectors.",
                'details': f"Recommended: Keep sector exposure below 40%"
            })
        
        # Check for small portfolio
        if metrics['total_holdings'] < 5:
            risks.append({
                'type': 'info',
                'icon': '💡',
                'title': 'Limited Holdings',
                'message': f"With only {metrics['total_holdings']} holdings, your portfolio may be more volatile. Consider adding 5-10 more stocks.",
                'details': "Diversification reduces risk"
            })
        
        return risks
    
    def _create_performance_insight(self, metrics):
        """Create performance insight"""
        portfolio = metrics['portfolio']
        
        if not portfolio:
            return None
        
        # Calculate total gain/loss
        total_gain_loss = sum(h['gain_loss'] for h in portfolio)
        total_cost = sum(h['purchase_price'] * h['shares'] for h in portfolio)
        total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        # Find best and worst performers
        best = max(portfolio, key=lambda x: x['gain_loss_pct'])
        worst = min(portfolio, key=lambda x: x['gain_loss_pct'])
        
        if total_gain_loss_pct > 5:
            icon = '📈'
            type_class = 'success'
            title = 'Strong Performance'
        elif total_gain_loss_pct > 0:
            icon = '📊'
            type_class = 'info'
            title = 'Positive Performance'
        elif total_gain_loss_pct > -5:
            icon = '📉'
            type_class = 'info'
            title = 'Slight Decline'
        else:
            icon = '📉'
            type_class = 'warning'
            title = 'Underperforming'
        
        return {
            'type': type_class,
            'icon': icon,
            'title': title,
            'message': f"Your portfolio is {'up' if total_gain_loss_pct > 0 else 'down'} {abs(total_gain_loss_pct):.1f}% (${total_gain_loss:,.2f}).",
            'details': f"Best: {best['ticker']} (+{best['gain_loss_pct']:.1f}%) | Worst: {worst['ticker']} ({worst['gain_loss_pct']:.1f}%)"
        }
    
    def _generate_ai_insights(self, portfolio, metrics):
        """Generate AI-powered insights using Perplexity"""
        if not portfolio:
            return []
        
        try:
            # Build portfolio summary for AI
            holdings_summary = []
            for h in portfolio[:10]:  # Limit to top 10 for prompt
                holdings_summary.append(
                    f"- {h['ticker']}: {h['shares']} shares, ${h['current_value']:,.2f} ({h['current_value']/metrics['total_value']*100:.1f}%)"
                )
            
            sector_summary = ", ".join([f"{k}: {v:.1f}%" for k, v in metrics['sectors'].items()])
            
            prompt = f"""Analyze this investment portfolio and provide 1-2 specific, actionable recommendations:

Portfolio Summary:
Total Value: ${metrics['total_value']:,.2f}
Holdings: {metrics['total_holdings']}
Diversification Score: {metrics['diversification_score']}/100

Top Holdings:
{chr(10).join(holdings_summary)}

Sector Allocation: {sector_summary}

Provide:
1. One specific recommendation to improve the portfolio
2. One strength or opportunity

Keep each point to 1-2 sentences. Be specific and actionable."""

            response = self.perplexity.query(prompt)
            content = response['content']
            
            # Parse AI response into insights
            insights = []
            
            # Simple parsing - split by numbers or bullet points
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            for i, line in enumerate(lines[:2]):  # Max 2 insights
                # Remove numbering
                line = line.lstrip('0123456789.-) ')
                
                if len(line) > 20:  # Valid insight
                    insights.append({
                        'type': 'info' if i == 1 else 'success',
                        'icon': '💡' if i == 0 else '🏆',
                        'title': 'AI Recommendation' if i == 0 else 'Portfolio Strength',
                        'message': line,
                        'details': 'Powered by AI analysis'
                    })
            
            return insights
            
        except Exception as e:
            print(f"AI insights error: {e}")
            # Return fallback insight
            return [{
                'type': 'info',
                'icon': '💡',
                'title': 'Portfolio Tip',
                'message': 'Regular portfolio rebalancing helps maintain your target asset allocation and manage risk.',
                'details': 'Review your portfolio quarterly'
            }]

# Singleton instance
portfolio_insights_service = PortfolioInsightsService()
