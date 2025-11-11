import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../services/api'

export default function ChatInterface({ ticker }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !ticker) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage(ticker, input)
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        citations: response.citations
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'error',
        content: error.message || 'Failed to get response'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-chat">
            <h3>💬 Free Chat Mode</h3>
            <p>Ask any question about {ticker || 'a stock'}</p>
            <div className="example-questions">
              <p>Try asking:</p>
              <ul>
                <li>"What are the main revenue streams?"</li>
                <li>"How does the company compare to competitors?"</li>
                <li>"What are the biggest risks?"</li>
                <li>"Is the stock overvalued?"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>
            {msg.citations && msg.citations.length > 0 && (
              <div className="message-citations">
                <details>
                  <summary>Sources ({msg.citations.length})</summary>
                  <ul>
                    {msg.citations.map((citation, i) => (
                      <li key={i}>
                        <a href={citation} target="_blank" rel="noopener noreferrer">
                          {citation}
                        </a>
                      </li>
                    ))}
                  </ul>
                </details>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={ticker ? `Ask about ${ticker}...` : 'Enter a ticker first...'}
          disabled={!ticker || loading}
          rows={3}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || !ticker || loading}
        >
          Send
        </button>
      </div>
    </div>
  )
}
