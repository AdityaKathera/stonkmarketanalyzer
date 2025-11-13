import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import ResearchFlow from './components/ResearchFlow'
import StockComparison from './components/StockComparison'
import Watchlist from './components/Watchlist'
import Portfolio from './components/PortfolioEnhanced'
import Profile from './components/Profile'
import NewsSection from './components/NewsSection'
import SocialSentiment from './components/SocialSentiment'
import FloatingChat from './components/FloatingChat'
import AuthModal from './components/AuthModal'
import StockChart from './components/StockChart'
import MarketOverview from './components/MarketOverview'
import AIInsights from './components/AIInsights'
import analytics from './analytics'
import './App.css'

function App() {
  const [mode, setMode] = useState('guided') // 'guided', 'watchlist', 'portfolio', 'market', 'insights'
  const [ticker, setTicker] = useState('')
  const [horizon, setHorizon] = useState('1-3 years')
  const [riskLevel, setRiskLevel] = useState('moderate')
  const [darkMode, setDarkMode] = useState(false)
  const [user, setUser] = useState(null)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  // Track page view on mount and check for existing auth
  useEffect(() => {
    analytics.trackPageView('home');
    
    // Check for existing auth token
    const token = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Cmd/Ctrl + K - Focus ticker input
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector('input[type="text"]')?.focus();
      }
      
      // Cmd/Ctrl + 1/2/3/4 - Switch modes
      if ((e.metaKey || e.ctrlKey) && ['1', '2', '3', '4'].includes(e.key)) {
        e.preventDefault();
        const modes = ['guided', 'chat', 'compare', 'watchlist'];
        const modeIndex = parseInt(e.key) - 1;
        if (modes[modeIndex]) {
          handleModeChange(modes[modeIndex]);
        }
      }
      
      // Escape - Clear ticker
      if (e.key === 'Escape') {
        setTicker('');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
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

  // Handle authentication success
  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuthModal(false);
  };

  // Handle user update (from profile)
  const handleUpdateUser = (updatedUser) => {
    setUser(updatedUser);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setUser(null);
    setMode('guided');
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
                <div className="market-indicators">
                  <div className="market-dot"></div>
                  <div className="market-dot"></div>
                  <div className="market-dot"></div>
                  <div className="market-line"></div>
                </div>
              </div>
            </div>
          </div>
          <div className="header-actions">
            {user ? (
              <div className="user-menu-container">
                <button 
                  className="profile-btn" 
                  onClick={() => setShowUserMenu(!showUserMenu)}
                >
                  👤 {user.name || user.email.split('@')[0]}
                </button>
                {showUserMenu && (
                  <div className="user-dropdown">
                    <button onClick={() => { handleModeChange('portfolio'); setShowUserMenu(false); }}>
                      💼 My Portfolio
                    </button>
                    <button onClick={() => { handleModeChange('insights'); setShowUserMenu(false); }}>
                      🧠 AI Insights
                    </button>
                    <div className="dropdown-divider"></div>
                    <button onClick={handleLogout}>
                      🚪 Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button className="login-btn" onClick={() => setShowAuthModal(true)}>
                Sign In
              </button>
            )}
            <button 
              className="theme-toggle" 
              onClick={handleDarkModeToggle}
              aria-label="Toggle dark mode"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
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
            📊 Research
          </button>
          <button
            className={mode === 'watchlist' ? 'active' : ''}
            onClick={() => handleModeChange('watchlist')}
          >
            ⭐ Watchlist
          </button>
          <button
            className={mode === 'market' ? 'active' : ''}
            onClick={() => handleModeChange('market')}
          >
            🌍 Market
          </button>
          {user && (
            <>
              <button
                className={mode === 'portfolio' ? 'active' : ''}
                onClick={() => handleModeChange('portfolio')}
              >
                💼 Portfolio
              </button>
              <button
                className={mode === 'insights' ? 'active' : ''}
                onClick={() => handleModeChange('insights')}
              >
                🧠 AI Insights
              </button>
            </>
          )}
        </div>
      </div>

      <main className="main-content">
        {mode === 'guided' && (
          <>
            <ResearchFlow ticker={ticker} horizon={horizon} riskLevel={riskLevel} />
            {ticker && <StockChart ticker={ticker} />}
          </>
        )}
        {mode === 'compare' && (
          <StockComparison />
        )}
        {mode === 'watchlist' && (
          <Watchlist onSelectStock={(t) => { setTicker(t); setMode('guided'); }} />
        )}
        {mode === 'market' && (
          <MarketOverview />
        )}
        {mode === 'portfolio' && user && (
          <Portfolio user={user} />
        )}
        {mode === 'insights' && user && (
          <AIInsights user={user} />
        )}
      </main>

      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Floating AI Chat Assistant */}
      <FloatingChat 
        currentMode={mode}
        ticker={ticker}
        user={user}
      />
    </div>
  )
}

export default App
