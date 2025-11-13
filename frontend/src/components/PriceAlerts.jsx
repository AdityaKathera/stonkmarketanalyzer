import { useState, useEffect } from 'react';
import './PriceAlerts.css';

export default function PriceAlerts({ user }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    ticker: '',
    alert_type: 'price',
    target_price: '',
    percentage_change: '',
    condition: 'above'
  });

  useEffect(() => {
    if (user) {
      fetchAlerts();
    }
  }, [user]);

  const fetchAlerts = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/alerts`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAlert = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/alerts`,
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
        fetchAlerts();
        setShowAddForm(false);
        setFormData({
          ticker: '',
          alert_type: 'price',
          target_price: '',
          percentage_change: '',
          condition: 'above'
        });
      }
    } catch (error) {
      console.error('Failed to add alert:', error);
    }
  };

  const handleDeleteAlert = async (alertId) => {
    if (!confirm('Delete this alert?')) return;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/alerts/${alertId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        fetchAlerts();
      }
    } catch (error) {
      console.error('Failed to delete alert:', error);
    }
  };

  if (!user) {
    return (
      <div className="price-alerts-container">
        <div className="auth-required">
          <p>Please sign in to set price alerts</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="price-alerts-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="price-alerts-container">
      <div className="alerts-header">
        <div>
          <h2>⚠️ Price Alerts</h2>
          <p>Get notified when stocks hit your target prices</p>
        </div>
        <button
          className="add-alert-btn"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? '✕ Cancel' : '+ New Alert'}
        </button>
      </div>

      {showAddForm && (
        <form className="add-alert-form" onSubmit={handleAddAlert}>
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
              <label>Alert Type</label>
              <select
                value={formData.alert_type}
                onChange={(e) => setFormData({...formData, alert_type: e.target.value})}
              >
                <option value="price">Price Target</option>
                <option value="percentage">Percentage Change</option>
              </select>
            </div>
          </div>

          {formData.alert_type === 'price' ? (
            <div className="form-row">
              <div className="form-field">
                <label>Target Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.target_price}
                  onChange={(e) => setFormData({...formData, target_price: e.target.value})}
                  placeholder="150.00"
                  required
                />
              </div>
              <div className="form-field">
                <label>Condition</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                >
                  <option value="above">Above</option>
                  <option value="below">Below</option>
                </select>
              </div>
            </div>
          ) : (
            <div className="form-row">
              <div className="form-field">
                <label>Percentage Change</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.percentage_change}
                  onChange={(e) => setFormData({...formData, percentage_change: e.target.value})}
                  placeholder="5.0"
                  required
                />
              </div>
              <div className="form-field">
                <label>Direction</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                >
                  <option value="up">Up</option>
                  <option value="down">Down</option>
                </select>
              </div>
            </div>
          )}

          <button type="submit" className="submit-btn">Create Alert</button>
        </form>
      )}

      {alerts.length === 0 ? (
        <div className="empty-alerts">
          <div className="empty-icon">🔔</div>
          <h3>No active alerts</h3>
          <p>Create your first price alert to get notified</p>
          <button
            className="add-first-alert-btn"
            onClick={() => setShowAddForm(true)}
          >
            Create Your First Alert
          </button>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert) => (
            <div key={alert.id} className={`alert-card ${alert.triggered ? 'triggered' : 'active'}`}>
              <div className="alert-header">
                <h3>{alert.ticker}</h3>
                <button
                  className="delete-btn"
                  onClick={() => handleDeleteAlert(alert.id)}
                  title="Delete alert"
                >
                  🗑️
                </button>
              </div>

              <div className="alert-details">
                {alert.alert_type === 'price' ? (
                  <div className="alert-condition">
                    Alert when price goes <strong>{alert.condition}</strong> <strong>${alert.target_price}</strong>
                  </div>
                ) : (
                  <div className="alert-condition">
                    Alert when price moves <strong>{alert.condition}</strong> by <strong>{alert.percentage_change}%</strong>
                  </div>
                )}

                <div className="alert-meta">
                  <span className={`status-badge ${alert.triggered ? 'triggered' : 'active'}`}>
                    {alert.triggered ? '✓ Triggered' : '● Active'}
                  </span>
                  <span className="created-date">
                    Created {new Date(alert.created_at).toLocaleDateString()}
                  </span>
                </div>

                {alert.triggered && alert.triggered_at && (
                  <div className="triggered-info">
                    Triggered on {new Date(alert.triggered_at).toLocaleString()}
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
