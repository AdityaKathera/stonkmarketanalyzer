import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 120000 // 2 minutes
})

export const executeGuidedStep = async (step, ticker, horizon, riskLevel) => {
  try {
    const response = await api.post('/api/research/guided', {
      step,
      ticker,
      horizon,
      riskLevel
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to execute research step')
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
