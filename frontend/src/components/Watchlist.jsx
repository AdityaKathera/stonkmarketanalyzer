import { useState, useEffect } from 'react'
import { executeGuidedStep } from '../services/api'
import analytics from '../analytics'
import './Watchlist.css'

function Watchlist({ onSelectStock }) {
  const [watchlist, setWatchlist] = useState([])
  const [newTicker, setNewTicker] = useState('')
  const [analyzing, setAnalyzing] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('stonk_watchlist')
    if (saved) {
      setWatchlist(JSON.parse(saved))
    }
  }, [])

  const saveWatchlist = (list) => {
    localStorage.setItem('stonk_watchlist', JSON.stringify(list))
    setWatchlist(list)
  }

  const addToWatchlist = () => {
    const ticker = newTicker.trim().toUpperCase()
    
    if (!ticker) return
    
    if (watchlist.some(item => item.ticker === ticker)) {
      alert('Stock already in watchlist')
      return
    }

    const newItem = {
      ticker,
      addedAt: new Date().toISOString(),
      lastAnalyzed: null
    }

    const updated = [...watchlist, newItem]
    saveWatchlist(updated)
    setNewTicker('')
    analytics.trackFeatureUse('watchlist_add', { ticker })
  }

  const removeFromWatchlist = (ticker) => {
    const updated = watchlist.filter(item => item.ticker !== ticker)
    saveWatchlist(updated)
    analytics.trackFeatureUse('watchlist_remove', { ticker })
  }

  const quickAnalyze = async (ticker) => {
    setAnalyzing(ticker)
    try {
      analytics.trackFeatureUse('watchlist_quick_analyze', { ticker })
      
      // Update last analyzed time
      const updated = watchlist.map(item => 
        item.ticker === ticker 
          ? { ...item, lastAnalyzed: new Date().toISOString() }
          : item
      )
      saveWatchlist(updated)
      
      // Trigger analysis in parent component
      if (onSelectStock) {
        onSelectStock(ticker)
      }
    } finally {
      setAnalyzing(null)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="watchlist">
      <div className="watchlist-header">
        <h2>⭐ My Watchlist</h2>
        <p>Track your favorite stocks</p>
      </div>

      <div className="add-stock">
        <input
          type="text"
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
          onKeyPress={(e) => e.key === 'Enter' && addToWatchlist()}
          placeholder="Add ticker (e.g., AAPL)"
          maxLength={5}
          className="watchlist-input"
        />
        <button onClick={addToWatchlist} className="add-btn">
          Add
        </button>
      </div>

      {watchlist.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <p>Your watchlist is empty</p>
          <p className="empty-hint">Add stocks to track them here</p>
        </div>
      ) : (
        <div className="watchlist-items">
          {watchlist.map((item) => (
            <div key={item.ticker} className="watchlist-item">
              <div className="item-info">
                <div className="item-ticker">{item.ticker}</div>
                <div className="item-meta">
                  Added {formatDate(item.addedAt)}
                  {item.lastAnalyzed && (
                    <span className="analyzed-badge">
                      Analyzed {formatDate(item.lastAnalyzed)}
                    </span>
                  )}
                </div>
              </div>
              <div className="item-actions">
                <button
                  onClick={() => quickAnalyze(item.ticker)}
                  disabled={analyzing === item.ticker}
                  className="analyze-btn"
                >
                  {analyzing === item.ticker ? '...' : '🔍'}
                </button>
                <button
                  onClick={() => removeFromWatchlist(item.ticker)}
                  className="remove-btn"
                  title="Remove from watchlist"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="watchlist-stats">
        <span>{watchlist.length} stock{watchlist.length !== 1 ? 's' : ''} tracked</span>
      </div>
    </div>
  )
}

export default Watchlist
