# Social Sentiment Tracker - Implementation Plan

## Overview
Track social media sentiment for portfolio stocks using AI-powered analysis. Show sentiment trends, popular mentions, and community mood.

## Features

### 1. Sentiment Analysis
- Overall sentiment score (0-100)
- Sentiment trend (Bullish/Bearish/Neutral)
- Sentiment change (↑ ↓ →)
- Community mood indicator

### 2. Social Metrics
- Mention volume (how often discussed)
- Engagement score (likes, shares, comments)
- Trending status (🔥 Hot, 📈 Rising, 📉 Cooling)
- Top keywords/hashtags

### 3. AI-Powered Insights
- Use Perplexity API to analyze current social sentiment
- Generate summary of community opinion
- Identify key discussion topics
- Detect sentiment shifts

### 4. Visual Display
- Sentiment gauge/meter
- Trend indicators
- Color-coded cards
- Comparison across portfolio stocks

## Implementation

### Backend (1.5 hours)

**File: `backend/social_sentiment_service.py`**
- Fetch social sentiment data
- Use Perplexity API to analyze current discussions
- Calculate sentiment scores
- Cache results (4 hours)

**Endpoints in `backend/auth_routes.py`**
- `GET /api/sentiment/stock/<ticker>` - Get sentiment for one stock
- `GET /api/sentiment/portfolio` - Get sentiment for all portfolio stocks
- `POST /api/sentiment/refresh` - Clear cache

### Frontend (1.5 hours)

**File: `frontend/src/components/SocialSentiment.jsx`**
- Display sentiment cards for each stock
- Sentiment gauge/meter
- Trend indicators
- Filter and sort options

**File: `frontend/src/components/SocialSentiment.css`**
- Beautiful card design
- Animated sentiment meters
- Color-coded sentiment indicators
- Dark mode support

### Integration (30 min)
- Add to main App.jsx navigation
- Add 📊 Sentiment tab

## Data Structure

```javascript
{
  ticker: "AAPL",
  sentiment: {
    score: 75,           // 0-100
    label: "Bullish",    // Bullish/Bearish/Neutral
    change: "+5",        // Change from previous
    trend: "up"          // up/down/stable
  },
  metrics: {
    mentions: 1250,      // Number of mentions
    engagement: "High",  // High/Medium/Low
    trending: "hot"      // hot/rising/cooling/stable
  },
  insights: {
    summary: "Community is bullish on AAPL...",
    topics: ["earnings", "iPhone sales", "AI"],
    mood: "Optimistic"
  },
  timestamp: "2024-11-13T10:00:00Z"
}
```

## UI Design

### Sentiment Card
```
┌─────────────────────────────────────┐
│ AAPL                    🔥 Hot      │
│                                     │
│     ┌─────────────┐                │
│     │   75/100    │  Bullish ↑     │
│     │  ●●●●●○○    │                │
│     └─────────────┘                │
│                                     │
│ 📊 1.2K mentions  💬 High engagement│
│                                     │
│ Community Mood: Optimistic          │
│ • Strong earnings expectations      │
│ • Positive iPhone 15 reviews        │
│ • AI features generating buzz       │
│                                     │
│ [View Details →]                    │
└─────────────────────────────────────┘
```

## Perplexity API Prompt

```
Analyze the current social media sentiment for {ticker} stock.

Provide:
1. Overall sentiment (Bullish/Bearish/Neutral) with score 0-100
2. Sentiment trend (Rising/Falling/Stable)
3. Top 3 discussion topics
4. Community mood (one word: Optimistic/Pessimistic/Cautious/Excited)
5. Brief summary (2-3 sentences)

Format:
SENTIMENT: [Bullish/Bearish/Neutral]
SCORE: [0-100]
TREND: [Rising/Falling/Stable]
TOPICS:
- Topic 1
- Topic 2
- Topic 3
MOOD: [One word]
SUMMARY: [2-3 sentences]
```

## Timeline

- Backend services: 1 hour
- API endpoints: 30 min
- Frontend component: 1 hour
- CSS styling: 30 min
- Integration: 30 min
- Testing & deployment: 30 min

**Total: ~4 hours**

## Success Criteria

- [ ] Sentiment scores calculated for all portfolio stocks
- [ ] AI-powered insights generated
- [ ] Beautiful visual display with gauges
- [ ] Trend indicators working
- [ ] Dark mode support
- [ ] Mobile responsive
- [ ] Deployed to production

---

**Ready to build!**
