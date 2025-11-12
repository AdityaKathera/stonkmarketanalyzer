import React, { useState, useEffect } from 'react';
import './LoadingAnalysis.css';

/**
 * LoadingAnalysis Component
 * Shows engaging loading state with progress for stock analysis
 * 
 * Security: No sensitive data displayed, client-side only
 */
export default function LoadingAnalysis({ ticker, step, onTimeout }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Initializing...');
  const [elapsed, setElapsed] = useState(0);
  
  useEffect(() => {
    const startTime = Date.now();
    
    // Progress stages with realistic timing
    const stages = [
      { time: 1000, status: '🔍 Fetching financial data...', progress: 15 },
      { time: 3000, status: '📊 Analyzing fundamentals...', progress: 30 },
      { time: 6000, status: '📈 Reviewing market trends...', progress: 45 },
      { time: 10000, status: '💡 Generating insights...', progress: 60 },
      { time: 15000, status: '📝 Compiling report...', progress: 75 },
      { time: 20000, status: '✨ Finalizing analysis...', progress: 85 },
      { time: 25000, status: '🎯 Almost done...', progress: 92 },
    ];
    
    const timers = stages.map(({ time, status, progress }) =>
      setTimeout(() => {
        setStatus(status);
        setProgress(progress);
      }, time)
    );
    
    // Update elapsed time every second
    const elapsedTimer = setInterval(() => {
      const seconds = Math.floor((Date.now() - startTime) / 1000);
      setElapsed(seconds);
      
      // Security: Timeout after 60 seconds (prevent hanging)
      if (seconds >= 60 && onTimeout) {
        onTimeout();
      }
    }, 1000);
    
    // Cleanup
    return () => {
      timers.forEach(clearTimeout);
      clearInterval(elapsedTimer);
    };
  }, [onTimeout]);
  
  // Calculate estimated time remaining
  const estimatedTotal = 30; // seconds
  const remaining = Math.max(0, estimatedTotal - elapsed);
  
  return (
    <div className="loading-analysis">
      <div className="loading-content">
        {/* Animated spinner */}
        <div className="spinner-container">
          <div className="spinner"></div>
          <div className="spinner-glow"></div>
        </div>
        
        {/* Stock info */}
        <h2 className="loading-title">
          Analyzing <span className="ticker-highlight">{ticker}</span>
        </h2>
        
        {/* Progress bar */}
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            >
              <div className="progress-shine"></div>
            </div>
          </div>
          <div className="progress-text">{progress}%</div>
        </div>
        
        {/* Status message */}
        <p className="status-message">{status}</p>
        
        {/* Time info */}
        <div className="time-info">
          <span className="elapsed">Elapsed: {elapsed}s</span>
          <span className="separator">•</span>
          <span className="remaining">~{remaining}s remaining</span>
        </div>
        
        {/* Helpful tip */}
        {elapsed > 10 && (
          <div className="tip">
            <span className="tip-icon">💡</span>
            <span className="tip-text">
              Tip: Popular stocks load instantly after the first analysis!
            </span>
          </div>
        )}
        
        {/* Warning if taking too long */}
        {elapsed > 40 && (
          <div className="warning">
            <span className="warning-icon">⚠️</span>
            <span className="warning-text">
              This is taking longer than usual. The AI is working hard on your analysis...
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
