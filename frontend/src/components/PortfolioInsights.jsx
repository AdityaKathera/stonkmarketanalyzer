import { useState, useEffect } from 'react';
import './PortfolioInsights.css';

function PortfolioInsights({ userId }) {
  const [insights, setInsights] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generatedAt, setGeneratedAt] = useState(null);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/insights`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch insights');
      }

      const data = await response.json();
      setInsights(data.insights || []);
      setSummary(data.summary || null);
      setGeneratedAt(data.generated_at);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchInsights();
    }
  }, [userId]);

  const handleRefresh = () => {
    fetchInsights();
  };

  const formatTime = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="portfolio-insights">
        <div className="insights-header">
          <h3>📊 Portfolio Insights</h3>
        </div>
        <div className="insights-loading">
          <div className="loading-spinner"></div>
          <p>Analyzing your portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="portfolio-insights">
        <div className="insights-header">
          <h3>📊 Portfolio Insights</h3>
        </div>
        <div className="insights-error">
          <p>⚠️ {error}</p>
          <button onClick={handleRefresh} className="refresh-btn">Try Again</button>
        </div>
      </div>
    );
  }

  if (!insights || insights.length === 0) {
    return (
      <div className="portfolio-insights">
        <div className="insights-header">
          <h3>📊 Portfolio Insights</h3>
        </div>
        <div className="insights-empty">
          <p>💡 Add stocks to your portfolio to get AI-powered insights!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-insights">
      <div className="insights-header">
        <div className="insights-title">
          <h3>📊 Portfolio Insights</h3>
          {generatedAt && (
            <span className="insights-time">Updated at {formatTime(generatedAt)}</span>
          )}
        </div>
        <button onClick={handleRefresh} className="refresh-btn" disabled={loading}>
          🔄 Refresh
        </button>
      </div>

      {summary && (
        <div className="insights-summary">
          <div className="summary-stat">
            <span className="stat-label">Total Value</span>
            <span className="stat-value">${summary.total_value?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Holdings</span>
            <span className="stat-value">{summary.total_holdings}</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Diversification</span>
            <span className="stat-value">{summary.diversification_score}/100</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Sectors</span>
            <span className="stat-value">{summary.sector_count}</span>
          </div>
        </div>
      )}

      <div className="insights-grid">
        {insights.map((insight, index) => (
          <div key={index} className={`insight-card insight-${insight.type}`}>
            <div className="insight-icon">{insight.icon}</div>
            <div className="insight-content">
              <h4 className="insight-title">{insight.title}</h4>
              <p className="insight-message">{insight.message}</p>
              {insight.details && (
                <p className="insight-details">{insight.details}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PortfolioInsights;
