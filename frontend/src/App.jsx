import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import ResearchFlow from './components/ResearchFlow'
import StockComparison from './components/StockComparison'
import Watchlist from './components/Watchlist'
import analytics from './analytics'
import './App.css'

function App() {
  const [mode, setMode] = useState('guided') // 'guided', 'chat', 'compare', 'watchlist'
  const [ticker, setTicker] = useState('')
  const [horizon, setHorizon] = useState('1-3 years')
  const [riskLevel, setRiskLevel] = useState('moderate')
  const [darkMode, setDarkMode] = useState(false)

  // Track page view on mount
  useEffect(() => {
    analytics.trackPageView('home');
  }, []);

  // Track mode changes
  const handleModeChange = (newMode) => {
    setMode(newMode);
    analytics.trackFeatureUse('mode_change', { mode: newMode });
  };

  // Track dark mode toggle
  const handleDarkModeToggle = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    analytics.trackSettings('dark_mode', newMode);
  };

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <div className="logo-icon">
                {/* Replace logo.png with your actual logo filename */}
                <img 
                  src="/logo.png" 
                  alt="Stonk Market Analyzer Logo" 
                  className="logo-image"
                  onError={(e) => {
                    // Fallback to emoji if image not found
                    e.target.style.display = 'none';
                    e.target.nextElementSibling.style.display = 'flex';
                  }}
                />
                <div className="logo-emoji-fallback" style={{display: 'none'}}>
                  <span className="logo-rocket">🚀</span>
                  <span className="logo-chart">📊</span>
                </div>
              </div>
              <div className="logo-text">
                <h1>STONK MARKET ANALYZER</h1>
                <p className="tagline">A prototype by Aditya Kathera</p>
              </div>
            </div>
          </div>
          <button 
            className="theme-toggle" 
            onClick={handleDarkModeToggle}
            aria-label="Toggle dark mode"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <div className="config-panel">
        <div className="input-group">
          <label>Ticker Symbol</label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="e.g., AAPL"
            maxLength={5}
          />
        </div>

        <div className="input-group">
          <label>Time Horizon</label>
          <select value={horizon} onChange={(e) => setHorizon(e.target.value)}>
            <option value="0-1 year">0-1 year</option>
            <option value="1-3 years">1-3 years</option>
            <option value="3-5 years">3-5 years</option>
            <option value="5+ years">5+ years</option>
          </select>
        </div>

        <div className="input-group">
          <label>Risk Tolerance</label>
          <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
            <option value="conservative">Conservative</option>
            <option value="moderate">Moderate</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </div>

        <div className="mode-toggle">
          <button
            className={mode === 'guided' ? 'active' : ''}
            onClick={() => handleModeChange('guided')}
          >
            📊 Guided
          </button>
          <button
            className={mode === 'chat' ? 'active' : ''}
            onClick={() => handleModeChange('chat')}
          >
            💬 Chat
          </button>
          <button
            className={mode === 'compare' ? 'active' : ''}
            onClick={() => handleModeChange('compare')}
          >
            ⚖️ Compare
          </button>
          <button
            className={mode === 'watchlist' ? 'active' : ''}
            onClick={() => handleModeChange('watchlist')}
          >
            ⭐ Watchlist
          </button>
        </div>
      </div>

      <main className="main-content">
        {mode === 'guided' && (
          <ResearchFlow ticker={ticker} horizon={horizon} riskLevel={riskLevel} />
        )}
        {mode === 'chat' && (
          <ChatInterface ticker={ticker} horizon={horizon} riskLevel={riskLevel} />
        )}
        {mode === 'compare' && (
          <StockComparison />
        )}
        {mode === 'watchlist' && (
          <Watchlist onSelectStock={(t) => { setTicker(t); setMode('guided'); }} />
        )}
      </main>
    </div>
  )
}

export default App
