import { useState, useEffect } from 'react';
import './MarketOverview.css';

export default function MarketOverview() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState('US');
  const [countries, setCountries] = useState([]);

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    fetchMarketData();
    const interval = setInterval(fetchMarketData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [selectedCountry]);

  const fetchCountries = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/market/countries`
      );

      if (response.ok) {
        const data = await response.json();
        setCountries(data.countries || []);
      }
    } catch (err) {
      console.error('Error fetching countries:', err);
    }
  };

  const fetchMarketData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/market/overview?country=${selectedCountry}`
      );

      if (!response.ok) throw new Error('Failed to fetch market data');

      const data = await response.json();
      setMarketData(data);
    } catch (err) {
      console.error('Market data fetch error:', err);
      setError('Market data unavailable');
    } finally {
      setLoading(false);
    }
  };

  const handleCountryChange = (country) => {
    setSelectedCountry(country);
  };

  if (loading && !marketData) {
    return (
      <div className="market-overview-container">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading market data...</p>
        </div>
      </div>
    );
  }

  if (error || !marketData) {
    return (
      <div className="market-overview-container">
        <div className="error">
          <p>{error || 'Market data unavailable'}</p>
        </div>
      </div>
    );
  }

  const { indices, movers, sectors, country_name } = marketData;

  return (
    <div className="market-overview-container">
      <div className="market-header">
        <div className="market-title-section">
          <h2>🌍 Market Overview</h2>
          <p>Real-time market data and trends</p>
        </div>
        
        {/* Country Selector */}
        {countries.length > 0 && (
          <div className="country-selector">
            {countries.map((country) => (
              <button
                key={country.code}
                className={`country-btn ${selectedCountry === country.code ? 'active' : ''}`}
                onClick={() => handleCountryChange(country.code)}
              >
                {country.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Current Country Display */}
      <div className="current-country">
        <span className="country-flag">{selectedCountry === 'US' ? '🇺🇸' : selectedCountry === 'IN' ? '🇮🇳' : '🇬🇧'}</span>
        <span className="country-name">{country_name}</span>
      </div>

      {/* Major Indices */}
      {indices && indices.length > 0 && (
        <div className="indices-section">
          <h3>Major Indices</h3>
          <div className="indices-grid">
            {indices.map((index) => {
              const isPositive = index.change >= 0;
              return (
                <div key={index.symbol} className={`index-card ${isPositive ? 'positive' : 'negative'}`}>
                  <div className="index-name">{index.name}</div>
                  <div className="index-symbol">{index.symbol}</div>
                  <div className="index-price">{index.price.toLocaleString()}</div>
                  <div className={`index-change ${isPositive ? 'positive' : 'negative'}`}>
                    {isPositive ? '▲' : '▼'} {Math.abs(index.change).toFixed(2)} ({Math.abs(index.change_percent).toFixed(2)}%)
                  </div>
                  {index.note && (
                    <div className="index-note">{index.note}</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Movers */}
      {movers && (movers.gainers?.length > 0 || movers.losers?.length > 0) && (
        <div className="movers-section">
          <div className="movers-grid">
            {movers.gainers && movers.gainers.length > 0 && (
              <div className="movers-column">
                <h3>📈 Top Gainers</h3>
                <div className="movers-list">
                  {movers.gainers.map((stock) => (
                    <div key={stock.ticker} className="mover-item positive">
                      <div className="mover-info">
                        <div className="mover-ticker">{stock.ticker}</div>
                        <div className="mover-name">{stock.name}</div>
                      </div>
                      <div className="mover-stats">
                        <div className="mover-price">${stock.price.toFixed(2)}</div>
                        <div className="mover-change positive">
                          +{stock.change_percent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {movers.losers && movers.losers.length > 0 && (
              <div className="movers-column">
                <h3>📉 Top Losers</h3>
                <div className="movers-list">
                  {movers.losers.map((stock) => (
                    <div key={stock.ticker} className="mover-item negative">
                      <div className="mover-info">
                        <div className="mover-ticker">{stock.ticker}</div>
                        <div className="mover-name">{stock.name}</div>
                      </div>
                      <div className="mover-stats">
                        <div className="mover-price">${stock.price.toFixed(2)}</div>
                        <div className="mover-change negative">
                          {stock.change_percent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* No Movers Message */}
      {movers && movers.gainers?.length === 0 && movers.losers?.length === 0 && (
        <div className="no-movers-message">
          <p>📊 Market movers data is being updated. Please check back in a few minutes.</p>
        </div>
      )}

      {/* Sector Performance */}
      {sectors && sectors.length > 0 && (
        <div className="sectors-section">
          <h3>Sector Performance</h3>
          <div className="sectors-grid">
            {sectors.map((sector) => {
              const isPositive = sector.change_percent >= 0;
              return (
                <div key={sector.name} className={`sector-card ${isPositive ? 'positive' : 'negative'}`}>
                  <div className="sector-name">{sector.name}</div>
                  <div className={`sector-change ${isPositive ? 'positive' : 'negative'}`}>
                    {isPositive ? '▲' : '▼'} {Math.abs(sector.change_percent).toFixed(2)}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="last-updated">
        Last updated: {new Date().toLocaleTimeString()} • Data cached for 5 minutes
      </div>
    </div>
  );
}
