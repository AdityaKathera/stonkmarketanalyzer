"""
Smart Rebalancing Service
Suggests exact trades to rebalance portfolio
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RebalancingService:
    """Smart portfolio rebalancing suggestions"""
    
    def generate_rebalancing_plan(self, portfolio_data: Dict, target_allocation: Optional[Dict] = None) -> Dict:
        """
        Generate specific trades to rebalance portfolio
        
        Args:
            portfolio_data: Current portfolio with holdings and prices
            target_allocation: Optional target percentages per holding
            
        Returns:
            Dict with trades, rationale, expected_outcome
        """
        try:
            holdings = portfolio_data.get('holdings', [])
            summary = portfolio_data.get('summary', {})
            total_value = summary.get('total_value', 0)
            
            if not holdings or total_value == 0:
                return {'trades': [], 'rationale': 'No holdings to rebalance', 'expected_outcome': {}}
            
            # Calculate current allocation
            current_allocation = self._calculate_current_allocation(holdings, total_value)
            
            # Determine target allocation
            if not target_allocation:
                target_allocation = self._suggest_target_allocation(holdings, total_value)
            
            # Generate trades
            trades = self._generate_trades(holdings, current_allocation, target_allocation, total_value)
            
            # Calculate expected outcome
            expected_outcome = self._calculate_expected_outcome(current_allocation, target_allocation, total_value)
            
            return {
                'trades': trades,
                'current_allocation': current_allocation,
                'target_allocation': target_allocation,
                'expected_outcome': expected_outcome,
                'rationale': self._generate_rationale(current_allocation, target_allocation),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating rebalancing plan: {str(e)}")
            return {'trades': [], 'rationale': 'Error generating plan', 'expected_outcome': {}}
    
    def _calculate_current_allocation(self, holdings: List[Dict], total_value: float) -> Dict:
        """Calculate current percentage allocation"""
        allocation = {}
        for holding in holdings:
            ticker = holding.get('ticker')
            current_value = holding.get('current_value', 0)
            percentage = (current_value / total_value * 100) if total_value > 0 else 0
            allocation[ticker] = {
                'percentage': round(percentage, 2),
                'value': current_value,
                'shares': holding.get('shares', 0),
                'price': holding.get('current_price', 0)
            }
        return allocation
    
    def _suggest_target_allocation(self, holdings: List[Dict], total_value: float) -> Dict:
        """Suggest balanced target allocation"""
        num_holdings = len(holdings)
        
        if num_holdings == 0:
            return {}
        
        # Equal weight as baseline
        equal_weight = 100 / num_holdings
        
        target = {}
        for holding in holdings:
            ticker = holding.get('ticker')
            
            # Adjust based on performance and size
            return_pct = holding.get('return_percentage', 0)
            current_pct = (holding.get('current_value', 0) / total_value * 100) if total_value > 0 else equal_weight
            
            # Winners get slightly more, losers get slightly less
            if return_pct > 20:
                target_pct = min(equal_weight * 1.2, 25)  # Max 25% per position
            elif return_pct < -15:
                target_pct = max(equal_weight * 0.8, 5)   # Min 5% per position
            else:
                target_pct = equal_weight
            
            target[ticker] = round(target_pct, 2)
        
        # Normalize to 100%
        total_target = sum(target.values())
        if total_target > 0:
            target = {k: round(v / total_target * 100, 2) for k, v in target.items()}
        
        return target
    
    def _generate_trades(self, holdings: List[Dict], current: Dict, target: Dict, total_value: float) -> List[Dict]:
        """Generate specific buy/sell trades"""
        trades = []
        
        for ticker in current.keys():
            current_pct = current[ticker]['percentage']
            target_pct = target.get(ticker, 0)
            diff_pct = target_pct - current_pct
            
            # Only suggest trades if difference > 5%
            if abs(diff_pct) < 5:
                continue
            
            current_value = current[ticker]['value']
            target_value = (target_pct / 100) * total_value
            diff_value = target_value - current_value
            
            current_price = current[ticker]['price']
            if current_price == 0:
                continue
            
            shares_to_trade = int(abs(diff_value) / current_price)
            
            if shares_to_trade == 0:
                continue
            
            trade_type = 'buy' if diff_value > 0 else 'sell'
            
            trades.append({
                'ticker': ticker,
                'action': trade_type,
                'shares': shares_to_trade,
                'estimated_price': current_price,
                'estimated_value': shares_to_trade * current_price,
                'current_allocation': current_pct,
                'target_allocation': target_pct,
                'reason': self._get_trade_reason(trade_type, current_pct, target_pct)
            })
        
        # Sort: sells first, then buys
        trades.sort(key=lambda x: (0 if x['action'] == 'sell' else 1, -x['estimated_value']))
        
        return trades
    
    def _get_trade_reason(self, action: str, current_pct: float, target_pct: float) -> str:
        """Generate human-readable reason for trade"""
        diff = abs(target_pct - current_pct)
        
        if action == 'sell':
            if current_pct > 30:
                return f'Overweight at {current_pct:.1f}% - reduce concentration risk'
            else:
                return f'Trim position from {current_pct:.1f}% to {target_pct:.1f}%'
        else:
            if current_pct < 10:
                return f'Underweight at {current_pct:.1f}% - increase exposure'
            else:
                return f'Increase position from {current_pct:.1f}% to {target_pct:.1f}%'
    
    def _calculate_expected_outcome(self, current: Dict, target: Dict, total_value: float) -> Dict:
        """Calculate expected outcome after rebalancing"""
        # Calculate diversification improvement
        current_std = self._calculate_allocation_std(current)
        target_std = self._calculate_allocation_std_from_pct(target)
        
        diversification_improvement = ((current_std - target_std) / current_std * 100) if current_std > 0 else 0
        
        # Calculate risk reduction
        max_current = max(h['percentage'] for h in current.values())
        max_target = max(target.values())
        risk_reduction = max_current - max_target
        
        return {
            'diversification_improvement': round(diversification_improvement, 1),
            'risk_reduction': round(risk_reduction, 1),
            'max_position_before': round(max_current, 1),
            'max_position_after': round(max_target, 1),
            'total_value_unchanged': total_value
        }
    
    def _calculate_allocation_std(self, allocation: Dict) -> float:
        """Calculate standard deviation of allocation percentages"""
        percentages = [h['percentage'] for h in allocation.values()]
        if not percentages:
            return 0
        
        mean = sum(percentages) / len(percentages)
        variance = sum((p - mean) ** 2 for p in percentages) / len(percentages)
        return variance ** 0.5
    
    def _calculate_allocation_std_from_pct(self, allocation: Dict) -> float:
        """Calculate standard deviation from percentage dict"""
        percentages = list(allocation.values())
        if not percentages:
            return 0
        
        mean = sum(percentages) / len(percentages)
        variance = sum((p - mean) ** 2 for p in percentages) / len(percentages)
        return variance ** 0.5
    
    def _generate_rationale(self, current: Dict, target: Dict) -> str:
        """Generate human-readable rationale"""
        num_holdings = len(current)
        max_current = max(h['percentage'] for h in current.values())
        max_target = max(target.values())
        
        rationale = f"Your portfolio has {num_holdings} holdings. "
        
        if max_current > 30:
            rationale += f"Your largest position is {max_current:.0f}% of your portfolio, which is high. "
        
        rationale += f"Rebalancing will create a more balanced allocation with a maximum position of {max_target:.0f}%, "
        rationale += "reducing concentration risk while maintaining your total portfolio value."
        
        return rationale


# Global instance
rebalancing_service = RebalancingService()
