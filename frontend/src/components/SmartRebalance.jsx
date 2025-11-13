import { useState, useEffect } from 'react';
import './SmartRebalance.css';

export default function SmartRebalance({ user }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchPlan();
    }
  }, [user]);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/rebalance`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPlan(data);
      }
    } catch (error) {
      console.error('Failed to fetch rebalancing plan:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="rebalance-container">
        <div className="auth-required">
          <p>Please sign in to see rebalancing suggestions</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rebalance-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Calculating optimal trades...</p>
        </div>
      </div>
    );
  }

  const { trades = [], rationale = '', expected_outcome = {}, current_allocation = {}, target_allocation = {} } = plan || {};

  if (trades.length === 0) {
    return (
      <div className="rebalance-container">
        <div className="rebalance-header">
          <h2>⚖️ Smart Rebalancing</h2>
          <p>Your portfolio is already well-balanced!</p>
        </div>
        <div className="no-rebalance">
          <div className="success-icon">✅</div>
          <h3>No rebalancing needed</h3>
          <p>Your current allocation is optimal. Check back after market movements.</p>
        </div>
      </div>
    );
  }

  const totalSellValue = trades.filter(t => t.action === 'sell').reduce((sum, t) => sum + t.estimated_value, 0);
  const totalBuyValue = trades.filter(t => t.action === 'buy').reduce((sum, t) => sum + t.estimated_value, 0);

  return (
    <div className="rebalance-container">
      <div className="rebalance-header">
        <div>
          <h2>⚖️ Smart Rebalancing</h2>
          <p>Optimize your portfolio allocation</p>
        </div>
        <button className="refresh-btn" onClick={fetchPlan}>
          🔄 Refresh
        </button>
      </div>

      {/* Rationale */}
      <div className="rationale-card">
        <h3>📊 Why Rebalance?</h3>
        <p>{rationale}</p>
      </div>

      {/* Expected Outcome */}
      {expected_outcome.diversification_improvement && (
        <div className="outcome-cards">
          <div className="outcome-card">
            <div className="outcome-label">Diversification</div>
            <div className="outcome-value positive">
              +{expected_outcome.diversification_improvement}%
            </div>
          </div>
          <div className="outcome-card">
            <div className="outcome-label">Risk Reduction</div>
            <div className="outcome-value positive">
              -{expected_outcome.risk_reduction}%
            </div>
          </div>
          <div className="outcome-card">
            <div className="outcome-label">Max Position</div>
            <div className="outcome-value">
              {expected_outcome.max_position_before}% → {expected_outcome.max_position_after}%
            </div>
          </div>
        </div>
      )}

      {/* Trades */}
      <div className="trades-section">
        <h3>📋 Recommended Trades</h3>
        <div className="trades-summary">
          <div className="summary-item">
            <span>Total to Sell:</span>
            <span className="sell-value">${totalSellValue.toFixed(0)}</span>
          </div>
          <div className="summary-item">
            <span>Total to Buy:</span>
            <span className="buy-value">${totalBuyValue.toFixed(0)}</span>
          </div>
        </div>

        <div className="trades-list">
          {trades.map((trade, index) => (
            <div key={index} className={`trade-card ${trade.action}`}>
              <div className="trade-header">
                <div className="trade-ticker">{trade.ticker}</div>
                <div className={`trade-action ${trade.action}`}>
                  {trade.action.toUpperCase()}
                </div>
              </div>
              <div className="trade-details">
                <div className="trade-shares">
                  {trade.shares} shares @ ${trade.estimated_price.toFixed(2)}
                </div>
                <div className="trade-value">
                  ${trade.estimated_value.toFixed(0)}
                </div>
              </div>
              <div className="trade-allocation">
                {trade.current_allocation.toFixed(1)}% → {trade.target_allocation.toFixed(1)}%
              </div>
              <div className="trade-reason">{trade.reason}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Allocation Comparison */}
      <div className="allocation-section">
        <h3>📊 Allocation Comparison</h3>
        <div className="allocation-grid">
          {Object.keys(current_allocation).map(ticker => (
            <div key={ticker} className="allocation-item">
              <div className="allocation-ticker">{ticker}</div>
              <div className="allocation-bars">
                <div className="allocation-bar current">
                  <div className="bar-fill" style={{ width: `${current_allocation[ticker].percentage}%` }}></div>
                  <span className="bar-label">{current_allocation[ticker].percentage.toFixed(1)}%</span>
                </div>
                <div className="allocation-bar target">
                  <div className="bar-fill" style={{ width: `${target_allocation[ticker]}%` }}></div>
                  <span className="bar-label">{target_allocation[ticker].toFixed(1)}%</span>
                </div>
              </div>
              <div className="allocation-labels">
                <span>Current</span>
                <span>Target</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
