"""
Social Sentiment Service - Track social media sentiment for stocks using AI
"""

import os
import requests
from typing import Dict, List
from datetime import datetime, timedelta

class SocialSentimentService:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.api_url = "https://api.perplexity.ai/chat/completions"
        
        # Cache: {ticker: {'data': {...}, 'timestamp': datetime}}
        self.cache = {}
        self.cache_duration = timedelta(hours=4)  # 4-hour cache
    
    def get_sentiment(self, ticker: str) -> Dict:
        """
        Get social sentiment analysis for a stock
        Returns sentiment data with AI insights
        """
        # Check cache
        if ticker in self.cache:
            cached = self.cache[ticker]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                print(f"[SocialSentiment] Cache hit for {ticker}")
                return cached['data']
        
        print(f"[SocialSentiment] Fetching sentiment for {ticker}")
        
        try:
            sentiment_data = self._analyze_sentiment(ticker)
            
            # Cache the result
            self.cache[ticker] = {
                'data': sentiment_data,
                'timestamp': datetime.now()
            }
            
            return sentiment_data
            
        except Exception as e:
            print(f"[SocialSentiment] Error: {e}")
            return self._get_fallback_sentiment(ticker)
    
    def get_portfolio_sentiment(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Get sentiment for multiple stocks
        Returns dict: {ticker: sentiment_data}
        """
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_sentiment(ticker)
        return results
    
    def _analyze_sentiment(self, ticker: str) -> Dict:
        """Use Perplexity AI to analyze social sentiment"""
        
        prompt = f"""Analyze the current social media and community sentiment for {ticker} stock.

Provide:
1. Overall sentiment (Bullish/Bearish/Neutral) with score 0-100
2. Sentiment trend compared to last week (Rising/Falling/Stable)
3. Top 3 discussion topics or themes
4. Community mood (one word: Optimistic/Pessimistic/Cautious/Excited/Uncertain)
5. Brief summary (2-3 sentences about what people are saying)

Format your response as:
SENTIMENT: [Bullish/Bearish/Neutral]
SCORE: [0-100]
TREND: [Rising/Falling/Stable]
TOPICS:
- [topic 1]
- [topic 2]
- [topic 3]
MOOD: [one word]
SUMMARY: [2-3 sentences]"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a social media sentiment analyst tracking stock discussions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the response
        return self._parse_sentiment_response(content, ticker)
    
    def _parse_sentiment_response(self, content: str, ticker: str) -> Dict:
        """Parse AI response into structured data"""
        lines = content.split('\n')
        
        sentiment_label = "Neutral"
        score = 50
        trend = "Stable"
        topics = []
        mood = "Cautious"
        summary = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('SENTIMENT:'):
                sentiment_label = line.replace('SENTIMENT:', '').strip()
            elif line.startswith('SCORE:'):
                try:
                    score = int(line.replace('SCORE:', '').strip())
                except:
                    score = 50
            elif line.startswith('TREND:'):
                trend = line.replace('TREND:', '').strip()
            elif line.startswith('TOPICS:'):
                current_section = 'topics'
            elif line.startswith('MOOD:'):
                mood = line.replace('MOOD:', '').strip()
                current_section = None
            elif line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
                current_section = 'summary'
            elif line.startswith('-') and current_section == 'topics':
                topics.append(line.replace('-', '').strip())
            elif current_section == 'summary' and not summary:
                summary = line
        
        # Determine trending status based on score and trend
        trending = self._calculate_trending(score, trend)
        
        # Calculate mentions (simulated based on score)
        mentions = self._estimate_mentions(score)
        
        # Determine engagement level
        engagement = self._calculate_engagement(score)
        
        return {
            'ticker': ticker,
            'sentiment': {
                'score': score,
                'label': sentiment_label,
                'change': self._calculate_change(trend),
                'trend': trend.lower()
            },
            'metrics': {
                'mentions': mentions,
                'engagement': engagement,
                'trending': trending
            },
            'insights': {
                'summary': summary or f"Community sentiment for {ticker} is {sentiment_label.lower()}.",
                'topics': topics[:3],
                'mood': mood
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_trending(self, score: int, trend: str) -> str:
        """Determine trending status"""
        if score >= 75 and trend.lower() == 'rising':
            return 'hot'
        elif score >= 60 and trend.lower() == 'rising':
            return 'rising'
        elif score <= 40 and trend.lower() == 'falling':
            return 'cooling'
        else:
            return 'stable'
    
    def _estimate_mentions(self, score: int) -> int:
        """Estimate mention volume based on sentiment score"""
        # Higher scores typically mean more discussion
        base = 500
        multiplier = score / 50
        return int(base * multiplier)
    
    def _calculate_engagement(self, score: int) -> str:
        """Calculate engagement level"""
        if score >= 70 or score <= 30:
            return 'High'  # Extreme sentiment = high engagement
        elif score >= 55 or score <= 45:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_change(self, trend: str) -> str:
        """Calculate sentiment change indicator"""
        trend = trend.lower()
        if trend == 'rising':
            return '+5'
        elif trend == 'falling':
            return '-5'
        else:
            return '0'
    
    def _get_fallback_sentiment(self, ticker: str) -> Dict:
        """Fallback sentiment when API fails"""
        return {
            'ticker': ticker,
            'sentiment': {
                'score': 50,
                'label': 'Neutral',
                'change': '0',
                'trend': 'stable'
            },
            'metrics': {
                'mentions': 500,
                'engagement': 'Medium',
                'trending': 'stable'
            },
            'insights': {
                'summary': f'Sentiment data for {ticker} is currently unavailable. Check back later for updates.',
                'topics': ['Market analysis', 'Price action', 'General discussion'],
                'mood': 'Neutral'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear all cached sentiment data"""
        self.cache = {}
        print("[SocialSentiment] Cache cleared")

# Singleton instance
_sentiment_service = None

def get_sentiment_service() -> SocialSentimentService:
    """Get or create SocialSentimentService singleton"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SocialSentimentService()
    return _sentiment_service
