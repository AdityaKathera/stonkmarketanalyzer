// Analytics tracking for Stonk Market Analyzer

class Analytics {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getUserId() {
    // Get or create persistent user ID
    let userId = localStorage.getItem('stonk_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('stonk_user_id', userId);
    }
    return userId;
  }

  // Track page views
  trackPageView(page) {
    this.track('page_view', {
      page,
      url: window.location.href,
      referrer: document.referrer
    });
  }

  // Track stock analysis
  trackStockAnalysis(ticker, step, success = true) {
    this.track('stock_analysis', {
      ticker,
      step,
      success,
      timestamp: new Date().toISOString()
    });
  }

  // Track feature usage
  trackFeatureUse(feature, data = {}) {
    this.track('feature_use', {
      feature,
      ...data
    });
  }

  // Track errors
  trackError(error, context = {}) {
    this.track('error', {
      error: error.message || error,
      stack: error.stack,
      ...context
    });
  }

  // Track user settings
  trackSettings(setting, value) {
    this.track('settings_change', {
      setting,
      value
    });
  }

  // Generic track function
  async track(eventName, data = {}) {
    const event = {
      event: eventName,
      userId: this.userId,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      screen: {
        width: window.screen.width,
        height: window.screen.height
      },
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      ...data
    };

    // Send to backend
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3001';
      await fetch(`${apiUrl}/api/analytics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(event)
      });
    } catch (error) {
      console.error('Analytics error:', error);
    }

    // Also log to console in development
    if (import.meta.env.DEV) {
      console.log('📊 Analytics:', eventName, data);
    }
  }
}

// Create singleton instance
const analytics = new Analytics();

// Track page visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    analytics.track('page_hidden');
  } else {
    analytics.track('page_visible');
  }
});

// Track session duration on page unload
window.addEventListener('beforeunload', () => {
  analytics.track('session_end');
});

export default analytics;
