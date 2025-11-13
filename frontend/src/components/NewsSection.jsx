import React, { useState, useEffect } from 'react';
import './NewsSection.css';

const NewsSection = () => {
  const [news, setNews] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTicker, setSelectedTicker] = useState('all');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchWatchlistNews();
  }, []);

  const fetchWatchlistNews = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('auth_token');
      const response = await fetch('https://api.stonkmarketanalyzer.com/api/news/watchlist?limit_per_stock=3', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }

      const data = await response.json();
      setNews(data.news || {});
      
      // Set first ticker as selected if available
      const tickers = Object.keys(data.news || {});
      if (tickers.length > 0 && selectedTicker === 'all') {
        setSelectedTicker(tickers[0]);
      }
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Failed to load news. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      
      const token = localStorage.getItem('auth_token');
      await fetch('https://api.stonkmarketanalyzer.com/api/news/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      await fetchWatchlistNews();
    } catch (err) {
      console.error('Error refreshing news:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    const s = sentiment?.toLowerCase() || 'neutral';
    if (s.includes('bullish') || s.includes('positive')) return 'bullish';
    if (s.includes('bearish') || s.includes('negative')) return 'bearish';
    return 'neutral';
  };

  const getSentimentEmoji = (sentiment) => {
    const s = sentiment?.toLowerCase() || 'neutral';
    if (s.includes('bullish') || s.includes('positive')) return '🟢';
    if (s.includes('bearish') || s.includes('negative')) return '🔴';
    return '⚪';
  };

  const getImpactBadge = (impact) => {
    const i = impact?.toLowerCase() || 'medium';
    if (i.includes('high')) return 'high';
    if (i.includes('low')) return 'low';
    return 'medium';
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return 'Recently';
    
    try {
      // Alpha Vantage format: 20241113T120000
      const year = timeStr.substring(0, 4);
      const month = timeStr.substring(4, 6);
      const day = timeStr.substring(6, 8);
      const hour = timeStr.substring(9, 11);
      const minute = timeStr.substring(11, 13);
      
      const date = new Date(`${year}-${month}-${day}T${hour}:${minute}:00`);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffHours / 24);
      
      if (diffHours < 1) return 'Just now';
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      
      return date.toLocaleDateString();
    } catch (e) {
      return 'Recently';
    }
  };

  const allTickers = Object.keys(news);
  const displayNews = selectedTicker === 'all' 
    ? Object.entries(news).flatMap(([ticker, items]) => 
        items.map(item => ({ ...item, ticker }))
      )
    : (news[selectedTicker] || []).map(item => ({ ...item, ticker: selectedTicker }));

  if (loading) {
    return (
      <div className="news-section">
        <div className="news-header">
          <h2>📰 AI News Summarizer</h2>
        </div>
        <div className="news-loading">
          <div className="spinner"></div>
          <p>Loading latest news...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="news-section">
        <div className="news-header">
          <h2>📰 AI News Summarizer</h2>
        </div>
        <div className="news-error">
          <p>{error}</p>
          <button onClick={fetchWatchlistNews} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (allTickers.length === 0) {
    return (
      <div className="news-section">
        <div className="news-header">
          <h2>📰 AI News Summarizer</h2>
        </div>
        <div className="news-empty">
          <p>📋 Add stocks to your watchlist to see personalized news!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="news-section">
      <div className="news-header">
        <h2>📰 AI News Summarizer</h2>
        <button 
          onClick={handleRefresh} 
          className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
          disabled={refreshing}
        >
          🔄 {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="news-filters">
        <button
          className={`filter-btn ${selectedTicker === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedTicker('all')}
        >
          All Stocks
        </button>
        {allTickers.map(ticker => (
          <button
            key={ticker}
            className={`filter-btn ${selectedTicker === ticker ? 'active' : ''}`}
            onClick={() => setSelectedTicker(ticker)}
          >
            {ticker}
          </button>
        ))}
      </div>

      <div className="news-grid">
        {displayNews.map((item, index) => (
          <div key={index} className="news-card">
            <div className="news-card-header">
              <span className="news-ticker">{item.ticker}</span>
              <span className="news-time">{formatTime(item.time_published)}</span>
            </div>

            <h3 className="news-title">{item.title}</h3>

            <div className="news-badges">
              <span className={`sentiment-badge ${getSentimentColor(item.ai_sentiment)}`}>
                {getSentimentEmoji(item.ai_sentiment)} {item.ai_sentiment || 'Neutral'}
              </span>
              <span className={`impact-badge ${getImpactBadge(item.ai_impact)}`}>
                Impact: {item.ai_impact || 'Medium'}
              </span>
            </div>

            <p className="news-summary">
              {item.ai_summary || item.summary || 'No summary available'}
            </p>

            {item.key_points && item.key_points.length > 0 && (
              <div className="news-key-points">
                <strong>Key Takeaways:</strong>
                <ul>
                  {item.key_points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="news-footer">
              <span className="news-source">📄 {item.source}</span>
              <a 
                href={item.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="read-more-btn"
              >
                Read Full Article →
              </a>
            </div>
          </div>
        ))}
      </div>

      {displayNews.length === 0 && (
        <div className="news-empty">
          <p>No news available for {selectedTicker}</p>
        </div>
      )}
    </div>
  );
};

export default NewsSection;
