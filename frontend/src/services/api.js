import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

// Test network connectivity
console.log('[API] Base URL:', API_BASE_URL)
console.log('[API] Environment:', import.meta.env.MODE)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 120000 // 2 minutes
})

export const executeGuidedStep = async (step, ticker, horizon, riskLevel) => {
  try {
    console.log('[API] Calling:', API_BASE_URL + '/api/research/guided')
    console.log('[API] Request:', { step, ticker, horizon, riskLevel })
    
    const response = await api.post('/api/research/guided', {
      step,
      ticker,
      horizon,
      riskLevel
    })
    
    console.log('[API] Success:', response.status)
    return response.data
  } catch (error) {
    console.error('[API] Error:', error.message)
    console.error('[API] Error details:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })
    
    const errorMsg = error.response?.data?.error || error.message || 'Failed to execute research step'
    throw new Error(errorMsg)
  }
}

export const sendChatMessage = async (ticker, question) => {
  try {
    const response = await api.post('/api/research/chat', {
      ticker,
      question
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to send message')
  }
}

export const getTemplates = async () => {
  try {
    const response = await api.get('/api/research/templates')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to fetch templates')
  }
}

export const compareStocks = async (tickers) => {
  try {
    const response = await api.post('/api/research/compare', { tickers })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to compare stocks')
  }
}
