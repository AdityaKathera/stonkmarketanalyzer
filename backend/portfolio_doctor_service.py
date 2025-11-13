"""
AI Portfolio Doctor Service
Provides daily actionable recommendations and health checks
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from services.perplexity_service import PerplexityService
import os

logger = logging.getLogger(__name__)

class PortfolioDoctorService:
    """AI-powered portfolio health and recommendations"""
    
    def __init__(self):
        self.perplexity = PerplexityService(os.getenv('PERPLEXITY_API_KEY'))
    
    def get_daily_recommendations(self, portfolio_data: Dict) -> Dict:
        """
        Generate daily actionable recommendations
        
        Args:
            portfolio_data: Dict with holdings, prices, performance
            
        Returns:
            Dict with action_items, risk_alerts, opportunities
        """
        try:
            holdings = portfolio_data.get('holdings', [])
            summary = portfolio_data.get('summary', {})
            
            if not holdings:
                return {
                    'action_items': [{
                        'type': 'start',
                        'priority': 'high',
                        'ticker': '',
                        'title': 'Start building your portfolio',
                        'description': 'Add your first stock to get personalized recommendations',
                        'action': 'Go to Portfolio and add your holdings',
                        'reasoning': 'Portfolio Doctor needs your holdings to provide personalized advice'
                    }],
                    'risk_alerts': [],
                    'opportunities': [],
                    'health_score': 50,
                    'generated_at': datetime.now().isoformat()
                }
            
            # Generate AI recommendations
            action_items = self._generate_action_items(holdings, summary)
            risk_alerts = self._generate_risk_alerts(holdings, summary)
            opportunities = self._generate_opportunities(holdings, summary)
            health_score = self._calculate_health_score(holdings, summary)
            
            return {
                'action_items': action_items,
                'risk_alerts': risk_alerts,
                'opportunities': opportunities,
                'health_score': health_score,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._get_fallback_recommendations()
    
    def _generate_action_items(self, holdings: List[Dict], summary: Dict) -> List[Dict]:
        """Generate specific action items for today"""
        actions = []
        
        for holding in holdings:
            ticker = holding.get('ticker')
            return_pct = holding.get('return_percentage', 0)
            current_price = holding.get('current_price')
            
            # Profit taking opportunity
            if return_pct > 30:
                actions.append({
                    'type': 'profit_taking',
                    'priority': 'high',
                    'ticker': ticker,
                    'title': f'Consider taking profits on {ticker}',
                    'description': f'Up {return_pct:.1f}% - consider selling 20-30% to lock in gains',
                    'action': f'Sell 20-30% of {ticker} position',
                    'reasoning': 'Strong gains achieved, reduce risk by taking partial profits'
                })
            
            # Buy the dip opportunity
            elif return_pct < -15:
                actions.append({
                    'type': 'buy_dip',
                    'priority': 'medium',
                    'ticker': ticker,
                    'title': f'{ticker} is down - potential entry point',
                    'description': f'Down {abs(return_pct):.1f}% - may be oversold',
                    'action': f'Consider averaging down on {ticker}',
                    'reasoning': 'Significant dip may present buying opportunity if fundamentals remain strong'
                })
            
            # Hold recommendation
            elif -5 <= return_pct <= 15:
                actions.append({
                    'type': 'hold',
                    'priority': 'low',
                    'ticker': ticker,
                    'title': f'Hold {ticker}',
                    'description': f'Currently {return_pct:+.1f}% - performing as expected',
                    'action': f'Continue holding {ticker}',
                    'reasoning': 'Position is stable, no action needed'
                })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return actions[:5]  # Top 5 actions
    
    def _generate_risk_alerts(self, holdings: List[Dict], summary: Dict) -> List[Dict]:
        """Generate risk alerts"""
        alerts = []
        
        # Concentration risk
        if len(holdings) < 5:
            alerts.append({
                'type': 'concentration',
                'severity': 'high',
                'title': 'Portfolio too concentrated',
                'description': f'Only {len(holdings)} holdings - high risk',
                'recommendation': 'Consider diversifying into 8-12 different stocks',
                'icon': '⚠️'
            })
        
        # Check for single stock > 30% of portfolio
        total_value = summary.get('total_value', 0)
        if total_value > 0:
            for holding in holdings:
                position_pct = (holding.get('current_value', 0) / total_value) * 100
                if position_pct > 30:
                    alerts.append({
                        'type': 'overweight',
                        'severity': 'medium',
                        'title': f'{holding["ticker"]} is {position_pct:.0f}% of portfolio',
                        'description': 'Single position risk is high',
                        'recommendation': f'Consider reducing {holding["ticker"]} to 15-20% of portfolio',
                        'icon': '🔴'
                    })
        
        # Large unrealized losses
        total_loss = sum(h.get('unrealized_gain', 0) for h in holdings if h.get('unrealized_gain', 0) < 0)
        if total_loss < -1000:
            alerts.append({
                'type': 'losses',
                'severity': 'medium',
                'title': f'Unrealized losses: ${abs(total_loss):,.0f}',
                'description': 'Significant paper losses in portfolio',
                'recommendation': 'Review losing positions - consider tax loss harvesting',
                'icon': '📉'
            })
        
        return alerts[:3]  # Top 3 alerts
    
    def _generate_opportunities(self, holdings: List[Dict], summary: Dict) -> List[Dict]:
        """Generate opportunity alerts"""
        opportunities = []
        
        # Tax loss harvesting
        for holding in holdings:
            if holding.get('return_percentage', 0) < -10:
                opportunities.append({
                    'type': 'tax_loss',
                    'value': 'high',
                    'ticker': holding['ticker'],
                    'title': f'Tax loss harvesting: {holding["ticker"]}',
                    'description': f'Down {abs(holding["return_percentage"]):.1f}% - can offset gains',
                    'action': 'Sell to realize loss, buy back after 31 days',
                    'potential_savings': abs(holding.get('unrealized_gain', 0)) * 0.2,  # Rough 20% tax
                    'icon': '💰'
                })
        
        # Stop loss suggestions
        for holding in holdings:
            if holding.get('return_percentage', 0) > 20 and not holding.get('has_stop_loss'):
                opportunities.append({
                    'type': 'stop_loss',
                    'value': 'medium',
                    'ticker': holding['ticker'],
                    'title': f'Set stop-loss for {holding["ticker"]}',
                    'description': f'Up {holding["return_percentage"]:.1f}% - protect your gains',
                    'action': f'Set stop-loss at {holding["current_price"] * 0.9:.2f} (10% below current)',
                    'icon': '🛡️'
                })
        
        # Rebalancing opportunity
        if len(holdings) >= 3:
            opportunities.append({
                'type': 'rebalance',
                'value': 'medium',
                'title': 'Portfolio rebalancing recommended',
                'description': 'Winners have grown, losers have shrunk',
                'action': 'Review rebalancing suggestions',
                'icon': '⚖️'
            })
        
        return opportunities[:4]  # Top 4 opportunities
    
    def _calculate_health_score(self, holdings: List[Dict], summary: Dict) -> int:
        """Calculate portfolio health score 0-100"""
        if not holdings:
            return 50  # Neutral score for empty portfolio
        
        score = 100
        
        # Diversification (max -30 points)
        if len(holdings) < 3:
            score -= 30
        elif len(holdings) < 5:
            score -= 20
        elif len(holdings) < 8:
            score -= 10
        
        # Performance (max -20 points)
        total_return = summary.get('total_return_percentage', 0)
        if total_return < -20:
            score -= 20
        elif total_return < -10:
            score -= 10
        elif total_return > 20:
            score += 5  # Bonus for good performance
        
        # Concentration risk (max -20 points)
        total_value = summary.get('total_value', 0)
        if total_value > 0 and len(holdings) > 0:
            try:
                max_position_pct = max((h.get('current_value', 0) / total_value) * 100 for h in holdings if h.get('current_value', 0) > 0)
                if max_position_pct > 40:
                    score -= 20
                elif max_position_pct > 30:
                    score -= 10
            except (ValueError, ZeroDivisionError):
                pass
        
        # Unrealized losses (max -15 points)
        if len(holdings) > 0:
            total_loss_pct = sum(1 for h in holdings if h.get('return_percentage', 0) < -15)
            if total_loss_pct > len(holdings) / 2:
                score -= 15
            elif total_loss_pct > len(holdings) / 3:
                score -= 10
        
        # Volatility (max -15 points)
        if len(holdings) > 0:
            high_volatility = sum(1 for h in holdings if abs(h.get('return_percentage', 0)) > 30)
            if high_volatility > len(holdings) / 2:
                score -= 15
        
        return max(0, min(100, score))
    
    def _get_fallback_recommendations(self) -> Dict:
        """Fallback recommendations if AI fails"""
        return {
            'action_items': [
                {
                    'type': 'review',
                    'priority': 'medium',
                    'title': 'Review your portfolio',
                    'description': 'Check your holdings and performance',
                    'action': 'Review each position',
                    'reasoning': 'Regular portfolio reviews help maintain healthy investments'
                }
            ],
            'risk_alerts': [],
            'opportunities': [],
            'health_score': 75,
            'generated_at': datetime.now().isoformat()
        }


# Global instance
portfolio_doctor = PortfolioDoctorService()
