import React, { useState, useEffect } from 'react';
import './SocialSentiment.css';

const SocialSentiment = () => {
  const [sentiment, setSentiment] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchPortfolioSentiment();
  }, []);

  const fetchPortfolioSentiment = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('auth_token');
      const response = await fetch('https://api.stonkmarketanalyzer.com/api/sentiment/portfolio', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sentiment');
      }

      const data = await response.json();
      setSentiment(data.sentiment || {});
    } catch (err) {
      console.error('Error fetching sentiment:', err);
      setError('Failed to load sentiment data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      
      const token = localStorage.getItem('auth_token');
      await fetch('https://api.stonkmarketanalyzer.com/api/sentiment/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      await fetchPortfolioSentiment();
    } catch (err) {
      console.error('Error refreshing sentiment:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const getSentimentColor = (score) => {
    if (score >= 70) return 'bullish';
    if (score <= 30) return 'bearish';
    return 'neutral';
  };

  const getTrendingIcon = (trending) => {
    switch (trending) {
      case 'hot': return '🔥';
      case 'rising': return '📈';
      case 'cooling': return '📉';
      default: return '📊';
    }
  };

  const getTrendingLabel = (trending) => {
    switch (trending) {
      case 'hot': return 'Hot';
      case 'rising': return 'Rising';
      case 'cooling': return 'Cooling';
      default: return 'Stable';
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'rising') return '↑';
    if (trend === 'falling') return '↓';
    return '→';
  };

  const formatMentions = (mentions) => {
    if (mentions >= 1000) {
      return `${(mentions / 1000).toFixed(1)}K`;
    }
    return mentions.toString();
  };

  const allTickers = Object.keys(sentiment);

  if (loading) {
    return (
      <div className="sentiment-section">
        <div className="sentiment-header">
          <h2>📊 Social Sentiment</h2>
        </div>
        <div className="sentiment-loading">
          <div className="spinner"></div>
          <p>Analyzing social sentiment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sentiment-section">
        <div className="sentiment-header">
          <h2>📊 Social Sentiment</h2>
        </div>
        <div className="sentiment-error">
          <p>{error}</p>
          <button onClick={fetchPortfolioSentiment} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (allTickers.length === 0) {
    return (
      <div className="sentiment-section">
        <div className="sentiment-header">
          <h2>📊 Social Sentiment</h2>
        </div>
        <div className="sentiment-empty">
          <p>💼 Add stocks to your portfolio to see social sentiment!</p>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '10px' }}>
            Track what the community is saying about your holdings.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="sentiment-section">
      <div className="sentiment-header">
        <h2>📊 Social Sentiment</h2>
        <button 
          onClick={handleRefresh} 
          className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
          disabled={refreshing}
        >
          🔄 {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="sentiment-grid">
        {allTickers.map((ticker) => {
          const data = sentiment[ticker];
          const sentimentColor = getSentimentColor(data.sentiment.score);
          
          return (
            <div key={ticker} className={`sentiment-card ${sentimentColor}`}>
              <div className="sentiment-card-header">
                <span className="sentiment-ticker">{ticker}</span>
                <span className={`trending-badge ${data.metrics.trending}`}>
                  {getTrendingIcon(data.metrics.trending)} {getTrendingLabel(data.metrics.trending)}
                </span>
              </div>

              <div className="sentiment-gauge-container">
                <div className="sentiment-gauge">
                  <div 
                    className={`sentiment-fill ${sentimentColor}`}
                    style={{ width: `${data.sentiment.score}%` }}
                  ></div>
                </div>
                <div className="sentiment-score-display">
                  <span className="score-number">{data.sentiment.score}</span>
                  <span className="score-label">/100</span>
                </div>
              </div>

              <div className="sentiment-label-row">
                <span className={`sentiment-label ${sentimentColor}`}>
                  {data.sentiment.label}
                </span>
                <span className={`sentiment-trend ${data.sentiment.trend}`}>
                  {getTrendIcon(data.sentiment.trend)} {data.sentiment.change}
                </span>
              </div>

              <div className="sentiment-metrics">
                <div className="metric">
                  <span className="metric-icon">💬</span>
                  <span className="metric-value">{formatMentions(data.metrics.mentions)}</span>
                  <span className="metric-label">mentions</span>
                </div>
                <div className="metric">
                  <span className="metric-icon">⚡</span>
                  <span className="metric-value">{data.metrics.engagement}</span>
                  <span className="metric-label">engagement</span>
                </div>
              </div>

              <div className="sentiment-insights">
                <div className="mood-badge">
                  Mood: <strong>{data.insights.mood}</strong>
                </div>
                <p className="insight-summary">{data.insights.summary}</p>
                
                {data.insights.topics && data.insights.topics.length > 0 && (
                  <div className="topics-list">
                    <strong>Top Topics:</strong>
                    <ul>
                      {data.insights.topics.map((topic, i) => (
                        <li key={i}>{topic}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SocialSentiment;
