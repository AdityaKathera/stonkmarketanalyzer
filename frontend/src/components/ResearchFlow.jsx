import { useState } from 'react'
import { executeGuidedStep } from '../services/api'
import analytics from '../analytics'
import LoadingAnalysis from './LoadingAnalysis'
import StockPriceHeader from './StockPriceHeader'

// Simple markdown-like formatter
const formatText = (text) => {
  if (!text) return null
  
  const lines = text.split('\n')
  const elements = []
  let currentList = []
  let listType = null
  
  lines.forEach((line, idx) => {
    // Headers (###, ##, or **)
    if (line.match(/^#{1,3}\s+(.+)/) || line.match(/^\*\*(.+)\*\*:?\s*$/)) {
      if (currentList.length > 0) {
        elements.push(<ul key={`list-${idx}`}>{currentList}</ul>)
        currentList = []
        listType = null
      }
      const headerText = line.replace(/^#{1,3}\s+/, '').replace(/^\*\*/, '').replace(/\*\*:?\s*$/, '').trim()
      elements.push(
        <h3 key={idx} className="section-header">
          <span className="header-icon">✦</span>
          {headerText}
        </h3>
      )
    }
    // Numbered lists
    else if (line.match(/^\d+\.\s+\*\*(.+?)\*\*:?\s*(.*)$/)) {
      if (listType !== 'numbered') {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`}>{currentList}</ul>)
        }
        currentList = []
        listType = 'numbered'
      }
      const match = line.match(/^\d+\.\s+\*\*(.+?)\*\*:?\s*(.*)$/)
      currentList.push(
        <li key={idx}>
          <strong>{match[1]}</strong>
          {match[2] && <span>: {match[2]}</span>}
        </li>
      )
    }
    // Bullet points
    else if (line.match(/^[-•]\s+(.+)$/)) {
      if (listType !== 'bullet') {
        if (currentList.length > 0) {
          elements.push(<ul key={`list-${idx}`}>{currentList}</ul>)
        }
        currentList = []
        listType = 'bullet'
      }
      const content = line.replace(/^[-•]\s+/, '')
      currentList.push(<li key={idx}>{formatInlineText(content)}</li>)
    }
    // Regular text
    else if (line.trim()) {
      if (currentList.length > 0) {
        elements.push(<ul key={`list-${idx}`}>{currentList}</ul>)
        currentList = []
        listType = null
      }
      elements.push(<p key={idx}>{formatInlineText(line)}</p>)
    }
    // Empty line
    else if (currentList.length > 0) {
      elements.push(<ul key={`list-${idx}`}>{currentList}</ul>)
      currentList = []
      listType = null
    }
  })
  
  if (currentList.length > 0) {
    elements.push(<ul key="list-final">{currentList}</ul>)
  }
  
  return elements
}

// Format inline bold text
const formatInlineText = (text) => {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx}>{part.slice(2, -2)}</strong>
    }
    return part
  })
}

const RESEARCH_STEPS = [
  { id: 'overview', name: 'Business Overview', icon: '🏢' },
  { id: 'financials', name: 'Financial Analysis', icon: '💰' },
  { id: 'moat', name: 'Competitive Moat', icon: '🏰' },
  { id: 'risks', name: 'Risk Assessment', icon: '⚠️' },
  { id: 'valuation', name: 'Valuation', icon: '📈' },
  { id: 'memo', name: 'Investment Memo', icon: '📝' },
  { id: 'investment_advice', name: 'Investment Advice by AI', icon: '🤖' }
]

export default function ResearchFlow({ ticker, horizon, riskLevel }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [results, setResults] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [analyzedParams, setAnalyzedParams] = useState({})

  const executeStep = async (stepId) => {
    if (!ticker) {
      setError('Please enter a ticker symbol')
      return
    }

    setLoading(true)
    setError(null)

    const startTime = Date.now();

    try {
      const response = await executeGuidedStep(stepId, ticker, horizon, riskLevel)
      setResults(prev => ({ ...prev, [stepId]: response }))
      setAnalyzedParams(prev => ({ 
        ...prev, 
        [stepId]: { ticker, horizon, riskLevel } 
      }))
      
      // Track successful analysis
      const duration = Date.now() - startTime;
      analytics.trackStockAnalysis(ticker, stepId, true);
      analytics.track('analysis_duration', { 
        ticker, 
        step: stepId, 
        duration,
        horizon,
        riskLevel
      });
    } catch (err) {
      console.error('Research step error:', err)
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      })
      const errorMsg = err.response?.data?.error || err.message || 'Failed to execute research step'
      setError(errorMsg)
      
      // Track failed analysis
      analytics.trackStockAnalysis(ticker, stepId, false);
      analytics.trackError(err, { ticker, step: stepId });
    } finally {
      setLoading(false)
    }
  }

  const reanalyzeStep = async (stepId) => {
    await executeStep(stepId)
  }

  const handleStepClick = async (index) => {
    setCurrentStep(index)
    const stepId = RESEARCH_STEPS[index].id
    if (!results[stepId]) {
      await executeStep(stepId)
    }
  }

  const currentStepData = RESEARCH_STEPS[currentStep]
  const currentResult = results[currentStepData.id]
  const analyzedParam = analyzedParams[currentStepData.id]
  
  const paramsChanged = analyzedParam && (
    analyzedParam.ticker !== ticker ||
    analyzedParam.horizon !== horizon ||
    analyzedParam.riskLevel !== riskLevel
  )

  return (
    <div className="research-flow">
      <div className="steps-sidebar">
        {RESEARCH_STEPS.map((step, index) => (
          <button
            key={step.id}
            className={`step-button ${currentStep === index ? 'active' : ''} ${results[step.id] ? 'completed' : ''}`}
            onClick={() => handleStepClick(index)}
            disabled={loading}
          >
            <span className="step-icon">{step.icon}</span>
            <span className="step-name">{step.name}</span>
            {results[step.id] && <span className="check">✓</span>}
          </button>
        ))}
      </div>

      <div className="step-content">
        <div className="step-header">
          <h2>{currentStepData.icon} {currentStepData.name}</h2>
          {ticker && <span className="ticker-badge">{ticker}</span>}
        </div>

        {/* Real-time Stock Price */}
        {ticker && !loading && <StockPriceHeader ticker={ticker} />}

        {error && <div className="error-message">{error}</div>}

        {loading && (
          <LoadingAnalysis 
            ticker={ticker} 
            step={currentStepData.name}
            onTimeout={() => {
              setLoading(false);
              setError('Analysis timed out. Please try again.');
            }}
          />
        )}

        {!loading && currentResult && (
          <div className="result-container">
            {paramsChanged && (
              <div className="ticker-change-banner">
                <div className="ticker-change-content">
                  <span className="ticker-change-icon">🔄</span>
                  <div>
                    <strong>Parameters Changed</strong>
                    <p>
                      Analysis was for: <span className="old-ticker">{analyzedParam.ticker}</span> 
                      {' '}({analyzedParam.horizon}, {analyzedParam.riskLevel})
                      <br />
                      Current selection: <span className="new-ticker">{ticker}</span>
                      {' '}({horizon}, {riskLevel})
                    </p>
                  </div>
                </div>
                <button 
                  className="reanalyze-button"
                  onClick={() => reanalyzeStep(currentStepData.id)}
                  disabled={!ticker}
                >
                  🔄 Reanalyze
                </button>
              </div>
            )}
            {currentStepData.id === 'investment_advice' && (
              <div className="disclaimer-banner">
                <div className="disclaimer-icon">⚠️</div>
                <div className="disclaimer-content">
                  <strong>IMPORTANT DISCLAIMER</strong>
                  <p>This is NOT financial advice and is generated by AI. The predictions and recommendations are for educational purposes only. Always consult with a qualified financial advisor before making investment decisions. Proceed with caution.</p>
                </div>
              </div>
            )}
            <div className="result-content formatted-content">
              {formatText(currentResult.response)}
            </div>
            {currentResult.citations && currentResult.citations.length > 0 && (
              <div className="citations">
                <h3>📚 Sources</h3>
                <ul>
                  {currentResult.citations.map((citation, idx) => (
                    <li key={idx}>
                      <a href={citation} target="_blank" rel="noopener noreferrer">
                        {citation}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {!loading && !currentResult && !error && (
          <div className="empty-state">
            <p>Click "Run Analysis" to start this research step</p>
            <button
              className="run-button"
              onClick={() => executeStep(currentStepData.id)}
              disabled={!ticker}
            >
              Run Analysis
            </button>
          </div>
        )}

        <div className="step-navigation">
          <button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0 || loading}
          >
            ← Previous
          </button>
          <button
            onClick={() => setCurrentStep(Math.min(RESEARCH_STEPS.length - 1, currentStep + 1))}
            disabled={currentStep === RESEARCH_STEPS.length - 1 || loading}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}
