import { useState, useEffect } from 'react';
import './Portfolio.css';

function PortfolioEnhanced({ user }) {
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [formData, setFormData] = useState({
    ticker: '',
    shares: '',
    purchase_price: '',
    purchase_date: '',
    notes: ''
  });

  useEffect(() => {
    fetchPortfolio();
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchPortfolio, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchPortfolio = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      else setRefreshing(true);
      
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/summary`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPortfolioData(data);
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAddStock = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(formData)
        }
      );

      if (response.ok) {
        fetchPortfolio();
        setShowAddForm(false);
        setFormData({
          ticker: '',
          shares: '',
          purchase_price: '',
          purchase_date: '',
          notes: ''
        });
      }
    } catch (error) {
      console.error('Failed to add stock:', error);
    }
  };

  const handleDelete = async (holdingId) => {
    if (!confirm('Are you sure you want to remove this holding?')) return;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/${holdingId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Failed to delete holding:', error);
    }
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="portfolio-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading portfolio...</p>
        </div>
      </div>
    );
  }

  const { holdings = [], summary = {} } = portfolioData || {};

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <div>
          <h2>📊 My Portfolio</h2>
          <p>Track your investments and performance</p>
        </div>
        <div className="header-actions">
          <button 
            className="refresh-btn"
            onClick={() => fetchPortfolio(false)}
            disabled={refreshing}
            title="Refresh prices"
          >
            {refreshing ? '⟳' : '🔄'} Refresh
          </button>
          <button 
            className="add-stock-btn"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? '✕ Cancel' : '+ Add Stock'}
          </button>
        </div>
      </div>

      {/* Portfolio Summary Cards */}
      {holdings.length > 0 && summary.total_value !== null && (
        <div className="portfolio-summary">
          <div className="summary-card">
            <div className="summary-label">Total Value</div>
            <div className="summary-value">{formatCurrency(summary.total_value)}</div>
          </div>
          <div className="summary-card">
            <div className="summary-label">Total Cost</div>
            <div className="summary-value">{formatCurrency(summary.total_cost)}</div>
          </div>
          <div className={`summary-card ${summary.total_gain >= 0 ? 'positive' : 'negative'}`}>
            <div className="summary-label">Total Gain/Loss</div>
            <div className="summary-value">
              {formatCurrency(summary.total_gain)}
              <span className="summary-percent">
                {formatPercent(summary.total_return_percentage)}
              </span>
            </div>
          </div>
          {summary.best_performer && (
            <div className="summary-card positive">
              <div className="summary-label">Best Performer</div>
              <div className="summary-value">
                {summary.best_performer.ticker}
                <span className="summary-percent">
                  {formatPercent(summary.best_performer.return_percentage)}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {showAddForm && (
        <form className="add-stock-form" onSubmit={handleAddStock}>
          <div className="form-row">
            <div className="form-field">
              <label>Ticker</label>
              <input
                type="text"
                value={formData.ticker}
                onChange={(e) => setFormData({...formData, ticker: e.target.value.toUpperCase()})}
                placeholder="AAPL"
                required
              />
            </div>
            <div className="form-field">
              <label>Shares</label>
              <input
                type="number"
                step="0.01"
                value={formData.shares}
                onChange={(e) => setFormData({...formData, shares: e.target.value})}
                placeholder="10"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Purchase Price</label>
              <input
                type="number"
                step="0.01"
                value={formData.purchase_price}
                onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                placeholder="150.00"
                required
              />
            </div>
            <div className="form-field">
              <label>Purchase Date</label>
              <input
                type="date"
                value={formData.purchase_date}
                onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label>Notes (Optional)</label>
            <input
              type="text"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Long-term hold, dividend stock, etc."
            />
          </div>

          <button type="submit" className="submit-btn">Add to Portfolio</button>
        </form>
      )}

      {holdings.length === 0 ? (
        <div className="empty-portfolio">
          <div className="empty-icon">📈</div>
          <h3>Your portfolio is empty</h3>
          <p>Start tracking your investments by adding your first stock</p>
          <button 
            className="add-first-stock-btn"
            onClick={() => setShowAddForm(true)}
          >
            Add Your First Stock
          </button>
        </div>
      ) : (
        <div className="portfolio-grid">
          {holdings.map((holding) => {
            const hasPrice = holding.current_price !== null;
            const isProfit = holding.unrealized_gain >= 0;
            
            return (
              <div key={holding.id} className={`portfolio-card ${hasPrice ? (isProfit ? 'profit' : 'loss') : ''}`}>
                <div className="card-header">
                  <h3>{holding.ticker}</h3>
                  <button 
                    className="delete-btn"
                    onClick={() => handleDelete(holding.id)}
                    title="Remove from portfolio"
                  >
                    🗑️
                  </button>
                </div>
                
                {hasPrice && (
                  <div className="card-performance">
                    <div className="current-price">
                      {formatCurrency(holding.current_price)}
                      <span className={`return-badge ${isProfit ? 'positive' : 'negative'}`}>
                        {formatPercent(holding.return_percentage)}
                      </span>
                    </div>
                    <div className="gain-loss">
                      {isProfit ? '↗' : '↘'} {formatCurrency(Math.abs(holding.unrealized_gain))}
                    </div>
                  </div>
                )}
                
                <div className="card-details">
                  <div className="detail-row">
                    <span className="label">Shares:</span>
                    <span className="value">{holding.shares}</span>
                  </div>
                  <div className="detail-row">
                    <span className="label">Purchase Price:</span>
                    <span className="value">{formatCurrency(holding.purchase_price)}</span>
                  </div>
                  {hasPrice && (
                    <>
                      <div className="detail-row">
                        <span className="label">Current Value:</span>
                        <span className="value">{formatCurrency(holding.current_value)}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Cost Basis:</span>
                        <span className="value">{formatCurrency(holding.cost_basis)}</span>
                      </div>
                    </>
                  )}
                  <div className="detail-row">
                    <span className="label">Purchase Date:</span>
                    <span className="value">{new Date(holding.purchase_date).toLocaleDateString()}</span>
                  </div>
                  {holding.notes && (
                    <div className="notes">
                      <span className="label">Notes:</span>
                      <p>{holding.notes}</p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {summary.last_updated && (
        <div className="last-updated">
          Last updated: {new Date(summary.last_updated).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}

export default PortfolioEnhanced;
