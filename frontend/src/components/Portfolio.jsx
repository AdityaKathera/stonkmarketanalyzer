import { useState, useEffect } from 'react';
import './Portfolio.css';

function Portfolio({ user }) {
  const [portfolio, setPortfolio] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    ticker: '',
    shares: '',
    purchase_price: '',
    purchase_date: '',
    notes: ''
  });

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPortfolio(data.holdings);
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStock = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

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
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/${holdingId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Failed to delete holding:', error);
    }
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

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <div>
          <h2>📊 My Portfolio</h2>
          <p>Track your investments and performance</p>
        </div>
        <button 
          className="add-stock-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ Add Stock'}
        </button>
      </div>

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

      {portfolio.length === 0 ? (
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
          {portfolio.map((holding) => (
            <div key={holding.id} className="portfolio-card">
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
              <div className="card-details">
                <div className="detail-row">
                  <span className="label">Shares:</span>
                  <span className="value">{holding.shares}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Purchase Price:</span>
                  <span className="value">${parseFloat(holding.purchase_price).toFixed(2)}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Total Cost:</span>
                  <span className="value">${(holding.shares * holding.purchase_price).toFixed(2)}</span>
                </div>
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
          ))}
        </div>
      )}
    </div>
  );
}

export default Portfolio;
