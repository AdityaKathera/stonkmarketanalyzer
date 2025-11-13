import { useState } from 'react';
import PortfolioDoctor from './PortfolioDoctor';
import SmartRebalance from './SmartRebalance';
import NewsSection from './NewsSection';
import SocialSentiment from './SocialSentiment';
import PriceAlerts from './PriceAlerts';
import './AIInsights.css';

export default function AIInsights({ user }) {
  const [activeTab, setActiveTab] = useState('doctor');

  const tabs = [
    { id: 'doctor', label: '🩺 Portfolio Doctor', component: PortfolioDoctor },
    { id: 'rebalance', label: '⚖️ Rebalancing', component: SmartRebalance },
    { id: 'news', label: '📰 News', component: NewsSection },
    { id: 'sentiment', label: '📊 Sentiment', component: SocialSentiment },
    { id: 'alerts', label: '⚠️ Alerts', component: PriceAlerts }
  ];

  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component;

  return (
    <div className="ai-insights-container">
      <div className="insights-header">
        <h1>🧠 AI Insights</h1>
        <p>Your personal AI financial advisor</p>
      </div>

      <div className="insights-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="insights-content">
        {ActiveComponent && <ActiveComponent user={user} />}
      </div>
    </div>
  );
}
