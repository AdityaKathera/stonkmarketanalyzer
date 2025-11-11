import { useState } from 'react'
import { compareStocks } from '../services/api'
import analytics from '../analytics'
import './StockComparison.css'

function StockComparison() {
  const [tickers, setTickers] = useState(['', '', ''])
  const [loading, setLoading] = useState(false)
  const [comparison, setComparison] = useState(null)
  const [error, setError] = useState(null)

  const handleTickerChange = (index, value) => {
    const newTickers = [...tickers]
    newTickers[index] = value.toUpperCase()
    setTickers(newTickers)
  }

  const handleCompare = async () => {
    const validTickers = tickers.filter(t => t.trim() !== '')
    
    if (validTickers.length < 2) {
      setError('Please enter at least 2 stock tickers')
      return
    }

    setLoading(true)
    setError(null)
    setComparison(null)
    
    try {
      analytics.trackFeatureUse('stock_comparison', { tickers: validTickers })
      const result = await compareStocks(validTickers)
      
      if (!result || !result.stocks) {
        throw new Error('Invalid response from server')
      }
      
      setComparison(result)
    } catch (err) {
      const errorMsg = err.message || 'Failed to compare stocks. Please try again.'
      setError(errorMsg)
      analytics.trackError('comparison_failed', errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="stock-comparison">
      <div className="comparison-header">
        <h2>📊 Compare Stocks</h2>
        <p>Compare up to 3 stocks side-by-side</p>
      </div>

      <div className="ticker-inputs">
        {tickers.map((ticker, index) => (
          <input
            key={index}
            type="text"
            value={ticker}
            onChange={(e) => handleTickerChange(index, e.target.value)}
            placeholder={`Stock ${index + 1} (e.g., AAPL)`}
            maxLength={5}
            className="ticker-input"
          />
        ))}
      </div>

      <button 
        onClick={handleCompare} 
        disabled={loading}
        className="compare-btn"
      >
        {loading ? '🔄 Analyzing stocks... (this may take 5-10 seconds)' : 'Compare Stocks'}
      </button>

      {loading && (
        <div className="loading-message">
          <div className="loading-spinner"></div>
          <p>AI is analyzing market data, financials, and trends...</p>
        </div>
      )}

      {error && <div className="error-message">❌ {error}</div>}

      {comparison && (
        <div className="comparison-results">
          {comparison.cached && (
            <div className="cache-badge">
              ⚡ Instant results from cache (analyzed within the last hour)
            </div>
          )}
          <div className="comparison-summary">
            <h3>Comparison Summary</h3>
            <div className="summary-text">{comparison.summary}</div>
          </div>

          <div className="comparison-grid">
            {comparison.stocks.map((stock, index) => (
              <div key={index} className="stock-card">
                <h4>{stock.ticker}</h4>
                <div className="stock-metrics">
                  <div className="metric">
                    <span className="metric-label">Recommendation</span>
                    <span className={`metric-value ${stock.recommendation.toLowerCase()}`}>
                      {stock.recommendation}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Risk Level</span>
                    <span className="metric-value">{stock.risk}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Growth Potential</span>
                    <span className="metric-value">{stock.growth}</span>
                  </div>
                </div>
                <div className="stock-highlights">
                  <h5>Key Points</h5>
                  <ul>
                    {stock.highlights.map((highlight, i) => (
                      <li key={i}>{highlight}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          <div className="winner-section">
            <h3>🏆 Best Choice</h3>
            <p>{comparison.winner}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default StockComparison
