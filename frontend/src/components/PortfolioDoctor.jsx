import { useState, useEffect } from 'react';
import './PortfolioDoctor.css';

export default function PortfolioDoctor({ user }) {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchRecommendations();
    }
  }, [user]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/portfolio/doctor`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="portfolio-doctor-container">
        <div className="auth-required">
          <p>Please sign in to see your portfolio recommendations</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="portfolio-doctor-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing your portfolio...</p>
        </div>
      </div>
    );
  }

  const { action_items = [], risk_alerts = [], opportunities = [], health_score = 0 } = recommendations || {};

  const getHealthColor = (score) => {
    if (score >= 80) return 'excellent';
    if (score >= 65) return 'good';
    if (score >= 50) return 'fair';
    return 'poor';
  };

  const getHealthLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 65) return 'Good';
    if (score >= 50) return 'Fair';
    if (score === 50) return 'Getting Started';
    return 'Needs Attention';
  };

  const getPriorityColor = (priority) => {
    if (priority === 'high') return 'priority-high';
    if (priority === 'medium') return 'priority-medium';
    return 'priority-low';
  };

  return (
    <div className="portfolio-doctor-container">
      <div className="doctor-header">
        <div>
          <h2>🩺 AI Portfolio Doctor</h2>
          <p>Your daily health check and action items</p>
        </div>
        <button className="refresh-btn" onClick={fetchRecommendations}>
          🔄 Refresh
        </button>
      </div>

      {/* Health Score */}
      <div className={`health-score-card ${getHealthColor(health_score)}`}>
        <div className="health-score-content">
          <div className="health-score-number">{health_score}</div>
          <div className="health-score-label">
            <div className="health-title">Portfolio Health Score</div>
            <div className="health-status">{getHealthLabel(health_score)}</div>
            <div className="health-description">
              {health_score >= 80 && "Your portfolio is well-balanced and healthy"}
              {health_score >= 65 && health_score < 80 && "Your portfolio is in good shape"}
              {health_score >= 50 && health_score < 65 && "Your portfolio needs some improvements"}
              {health_score < 50 && health_score > 0 && "Review the recommendations below"}
              {health_score === 50 && "Add stocks to get personalized analysis"}
            </div>
          </div>
        </div>
        <div className="health-bar">
          <div className="health-bar-fill" style={{ width: `${health_score}%` }}></div>
        </div>
      </div>

      {/* Action Items */}
      {action_items.length > 0 && (
        <div className="recommendations-section">
          <h3>📋 Today's Action Items</h3>
          <div className="action-items-list">
            {action_items.map((item, index) => (
              <div key={index} className={`action-item ${getPriorityColor(item.priority)}`}>
                <div className="action-header">
                  <div className="action-title">{item.title}</div>
                  <div className={`priority-badge ${item.priority}`}>
                    {item.priority}
                  </div>
                </div>
                <div className="action-description">{item.description}</div>
                <div className="action-recommendation">
                  <strong>Action:</strong> {item.action}
                </div>
                <div className="action-reasoning">
                  <em>{item.reasoning}</em>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Alerts */}
      {risk_alerts.length > 0 && (
        <div className="recommendations-section">
          <h3>⚠️ Risk Alerts</h3>
          <div className="risk-alerts-list">
            {risk_alerts.map((alert, index) => (
              <div key={index} className={`risk-alert severity-${alert.severity}`}>
                <div className="alert-icon">{alert.icon}</div>
                <div className="alert-content">
                  <div className="alert-title">{alert.title}</div>
                  <div className="alert-description">{alert.description}</div>
                  <div className="alert-recommendation">
                    <strong>Recommendation:</strong> {alert.recommendation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Opportunities */}
      {opportunities.length > 0 && (
        <div className="recommendations-section">
          <h3>💡 Opportunities</h3>
          <div className="opportunities-list">
            {opportunities.map((opp, index) => (
              <div key={index} className="opportunity-card">
                <div className="opp-icon">{opp.icon}</div>
                <div className="opp-content">
                  <div className="opp-title">{opp.title}</div>
                  <div className="opp-description">{opp.description}</div>
                  <div className="opp-action">
                    <strong>Action:</strong> {opp.action}
                  </div>
                  {opp.potential_savings && (
                    <div className="opp-savings">
                      Potential savings: ${opp.potential_savings.toFixed(0)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
