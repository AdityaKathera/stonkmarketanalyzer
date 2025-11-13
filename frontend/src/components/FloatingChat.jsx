import React, { useState, useEffect, useRef } from 'react';
import './FloatingChat.css';

const FloatingChat = ({ currentMode, ticker, user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        type: 'bot',
        text: "👋 Hi! I'm your AI stock assistant. Ask me anything about stocks, your portfolio, or market trends!",
        timestamp: new Date()
      }]);
    }
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Context-aware suggestions based on current page
  const getContextSuggestions = () => {
    switch (currentMode) {
      case 'portfolio':
        return [
          '📊 Analyze my portfolio',
          '💡 Give me investment tips',
          '📈 Which stocks should I buy?'
        ];
      case 'news':
        return [
          '📰 Summarize latest news',
          '🔍 What\'s trending today?',
          '💬 Explain this news impact'
        ];
      case 'sentiment':
        return [
          '🎭 Explain sentiment scores',
          '📊 What\'s the market mood?',
          '🔥 Which stocks are hot?'
        ];
      default:
        if (ticker) {
          return [
            `📊 Analyze ${ticker}`,
            `💰 Is ${ticker} a good buy?`,
            `📈 ${ticker} price prediction`
          ];
        }
        return [
          '🔍 Research a stock',
          '💼 Portfolio advice',
          '📊 Market analysis'
        ];
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setIsTyping(true);

    try {
      // Call AI chat API
      const token = localStorage.getItem('auth_token');
      const response = await fetch('https://api.stonkmarketanalyzer.com/api/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userInput,
          context: {
            mode: currentMode,
            ticker: ticker
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get AI response');
      }

      const data = await response.json();
      
      const botMessage = {
        type: 'bot',
        text: data.response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback response
      const botMessage = {
        type: 'bot',
        text: "I'm having trouble connecting right now. Please try again in a moment!",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button
        className={`floating-chat-button ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="AI Chat Assistant"
      >
        {isOpen ? '✕' : '💬'}
        {!isOpen && <span className="pulse-dot"></span>}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="floating-chat-panel">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-content">
              <span className="chat-icon">🤖</span>
              <div>
                <h3>Stonk AI Assistant</h3>
                <p>Powered by AI</p>
              </div>
            </div>
            <button className="chat-close" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <div className="message-bubble">
                  {msg.text}
                </div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot">
                <div className="message-bubble typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions */}
          {messages.length <= 2 && (
            <div className="chat-suggestions">
              {getContextSuggestions().map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="chat-input-container">
            <textarea
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about stocks..."
              rows="1"
            />
            <button
              className="chat-send"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChat;
