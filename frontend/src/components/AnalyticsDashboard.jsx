import { useState, useEffect } from 'react'
import axios from 'axios'

export default function AnalyticsDashboard() {
  const [stats, setStats] = useState(null)
  const [popularStocks, setPopularStocks] = useState([])
  const [loading, setLoading] = useState(true)

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const [statsRes, stocksRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/analytics/stats`),
        axios.get(`${API_BASE_URL}/api/analytics/popular-stocks`)
      ])
      
      setStats(statsRes.data)
      setPopularStocks(stocksRes.data.stocks)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="analytics-dashboard">Loading analytics...</div>
  }

  return (
    <div className="analytics-dashboard">
      <h2>📊 Analytics Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats?.unique_users || 0}</div>
          <div className="stat-label">Unique Users Today</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats?.unique_sessions || 0}</div>
          <div className="stat-label">Sessions Today</div>
        </div>
        
        <div className="stat-card">
          <div className="stat-value">{stats?.total_events || 0}</div>
          <div className="stat-label">Total Events</div>
        </div>
      </div>

      <div className="popular-stocks">
        <h3>🔥 Most Analyzed Stocks Today</h3>
        {popularStocks.length > 0 ? (
          <ul>
            {popularStocks.map((stock, idx) => (
              <li key={stock.ticker}>
                <span className="rank">#{idx + 1}</span>
                <span className="ticker">{stock.ticker}</span>
                <span className="count">{stock.count} analyses</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No stock analyses yet today</p>
        )}
      </div>

      <div className="event-breakdown">
        <h3>Event Breakdown</h3>
        {stats?.events && Object.keys(stats.events).length > 0 ? (
          <ul>
            {Object.entries(stats.events).map(([event, count]) => (
              <li key={event}>
                <span className="event-name">{event}</span>
                <span className="event-count">{count}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No events tracked yet</p>
        )}
      </div>
    </div>
  )
}
