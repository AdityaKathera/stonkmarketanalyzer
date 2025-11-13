"""
News Summarizer Service - AI-powered news summarization using Perplexity
"""

import os
import requests
from typing import Dict, List
from datetime import datetime, timedelta

class NewsSummarizerService:
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.api_url = "https://api.perplexity.ai/chat/completions"
        
        # Cache: {cache_key: {'summary': {...}, 'timestamp': datetime}}
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def summarize_news(self, news_item: Dict, ticker: str) -> Dict:
        """
        Summarize a single news article with AI
        Returns enhanced news item with AI summary, sentiment, and impact
        """
        # Create cache key
        cache_key = f"{ticker}_{news_item.get('url', '')}"
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now() - cached['timestamp'] < self.cache_duration:
                return cached['summary']
        
        # Get AI summary
        try:
            summary_data = self._get_ai_summary(news_item, ticker)
            
            # Enhance news item
            enhanced = {
                **news_item,
                'ai_summary': summary_data['summary'],
                'ai_sentiment': summary_data['sentiment'],
                'ai_impact': summary_data['impact'],
                'key_points': summary_data['key_points']
            }
            
            # Cache it
            self.cache[cache_key] = {
                'summary': enhanced,
                'timestamp': datetime.now()
            }
            
            return enhanced
            
        except Exception as e:
            print(f"[NewsSummarizer] Error: {e}")
            # Return with fallback data
            return {
                **news_item,
                'ai_summary': news_item.get('summary', 'Summary not available'),
                'ai_sentiment': self._parse_sentiment(news_item.get('sentiment_label', 'Neutral')),
                'ai_impact': 'Low',
                'key_points': [
                    'Click to view full details',
                    'Real-time market data available',
                    'Check for latest updates'
                ]
            }
    
    def summarize_multiple(self, news_items: List[Dict], ticker: str) -> List[Dict]:
        """Summarize multiple news articles"""
        return [self.summarize_news(item, ticker) for item in news_items]
    
    def _get_ai_summary(self, news_item: Dict, ticker: str) -> Dict:
        """Get AI-powered summary from Perplexity"""
        
        title = news_item.get('title', '')
        summary = news_item.get('summary', '')
        
        prompt = f"""Analyze this news article about {ticker} stock:

Title: {title}
Summary: {summary}

Provide:
1. A concise 2-3 sentence summary
2. Sentiment (Bullish/Bearish/Neutral)
3. Impact on stock price (High/Medium/Low)
4. 2-3 key takeaway points

Format your response as:
SUMMARY: [your summary]
SENTIMENT: [Bullish/Bearish/Neutral]
IMPACT: [High/Medium/Low]
KEY_POINTS:
- [point 1]
- [point 2]
- [point 3]"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial analyst providing concise stock news analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 300
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Parse the response
        return self._parse_ai_response(content)
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into structured data"""
        lines = content.split('\n')
        
        summary = ""
        sentiment = "Neutral"
        impact = "Medium"
        key_points = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
                current_section = 'summary'
            elif line.startswith('SENTIMENT:'):
                sentiment = line.replace('SENTIMENT:', '').strip()
                current_section = 'sentiment'
            elif line.startswith('IMPACT:'):
                impact = line.replace('IMPACT:', '').strip()
                current_section = 'impact'
            elif line.startswith('KEY_POINTS:'):
                current_section = 'key_points'
            elif line.startswith('-') and current_section == 'key_points':
                key_points.append(line.replace('-', '').strip())
            elif current_section == 'summary' and not summary:
                summary = line
        
        return {
            'summary': summary or "Analysis not available",
            'sentiment': sentiment,
            'impact': impact,
            'key_points': key_points[:3]  # Max 3 points
        }
    
    def _parse_sentiment(self, label: str) -> str:
        """Convert sentiment label to standard format"""
        label = label.lower()
        if 'bullish' in label or 'positive' in label:
            return 'Bullish'
        elif 'bearish' in label or 'negative' in label:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def clear_cache(self):
        """Clear all cached summaries"""
        self.cache = {}
        print("[NewsSummarizer] Cache cleared")

# Singleton instance
_summarizer_service = None

def get_summarizer_service() -> NewsSummarizerService:
    """Get or create NewsSummarizerService singleton"""
    global _summarizer_service
    if _summarizer_service is None:
        _summarizer_service = NewsSummarizerService()
    return _summarizer_service
