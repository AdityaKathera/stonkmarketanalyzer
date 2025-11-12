import React, { useState, useEffect } from 'react';
import './StockPriceHeader.css';

/**
 * StockPriceHeader Component
 * Displays real-time stock price with change indicators
 * 
 * Security: Validates ticker format, handles errors gracefully
 */
export default function StockPriceHeader({ ticker }) {
  const [priceData, setPriceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!ticker) {
      setLoading(false);
      return;
    }

    // Security: Validate ticker format
    if (!/^[A-Z]{1,5}$/.test(ticker.toUpperCase())) {
      setError('Invalid ticker format');
      setLoading(false);
      return;
    }

    fetchPrice();
    
    // Refresh price every 60 seconds
    const interval = setInterval(fetchPrice, 60000);
    
    return () => clearInterval(interval);
  }, [ticker]);

  const fetchPrice = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/stock/price/${ticker.toUpperCase()}`,
        { timeout: 5000 }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch price');
      }
      
      const data = await response.json();
      setPriceData(data);
    } catch (err) {
      console.error('Price fetch error:', err);
      setError('Price unavailable');
    } finally {
      setLoading(false);
    }
  };

  if (!ticker) return null;
  
  if (loading && !priceData) {
    return (
      <div className="stock-price-header loading">
        <div className="price-skeleton"></div>
      </div>
    );
  }

  if (error || !priceData) {
    return (
      <div className="stock-price-header error">
        <span className="ticker-symbol">{ticker}</span>
        <span className="price-error">Price data unavailable</span>
      </div>
    );
  }

  const isPositive = priceData.change >= 0;
  const changeIcon = isPositive ? '▲' : '▼';
  const changeClass = isPositive ? 'positive' : 'negative';

  return (
    <div className="stock-price-header">
      <div className="price-main">
        <span className="ticker-symbol">{priceData.symbol}</span>
        <span className="current-price">
          ${priceData.price.toFixed(2)}
          <span className="currency">{priceData.currency}</span>
        </span>
      </div>
      
      <div className={`price-change ${changeClass}`}>
        <span className="change-icon">{changeIcon}</span>
        <span className="change-amount">${Math.abs(priceData.change).toFixed(2)}</span>
        <span className="change-percent">({Math.abs(priceData.change_percent).toFixed(2)}%)</span>
      </div>
      
      <div className="price-meta">
        <span className="market-state">{priceData.market_state}</span>
        <span className="price-source">via {priceData.source}</span>
        {priceData.cached && <span className="cached-indicator">cached</span>}
      </div>
    </div>
  );
}
