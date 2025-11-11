"""Analytics tracking and storage for Stonk Market Analyzer"""

import json
import os
from datetime import datetime
from pathlib import Path

class AnalyticsService:
    """Simple file-based analytics storage"""
    
    def __init__(self):
        self.analytics_dir = Path('/opt/stonkmarketanalyzer/analytics')
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.daily_file = self.analytics_dir / f"analytics_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    
    def track_event(self, event_data):
        """Store analytics event"""
        try:
            # Add server timestamp
            event_data['server_timestamp'] = datetime.now().isoformat()
            
            # Append to daily file
            with open(self.daily_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
            
            return True
        except Exception as e:
            print(f"Analytics error: {e}")
            return False
    
    def get_stats(self, date=None):
        """Get analytics stats for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return {
                'date': date,
                'total_events': 0,
                'unique_users': 0,
                'unique_sessions': 0,
                'events': {}
            }
        
        events = []
        users = set()
        sessions = set()
        event_counts = {}
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    events.append(event)
                    
                    if 'userId' in event:
                        users.add(event['userId'])
                    if 'sessionId' in event:
                        sessions.add(event['sessionId'])
                    
                    event_name = event.get('event', 'unknown')
                    event_counts[event_name] = event_counts.get(event_name, 0) + 1
                except:
                    continue
        
        return {
            'date': date,
            'total_events': len(events),
            'unique_users': len(users),
            'unique_sessions': len(sessions),
            'events': event_counts
        }
    
    def get_popular_stocks(self, date=None, limit=10):
        """Get most analyzed stocks"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return []
        
        stock_counts = {}
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get('event') == 'stock_analysis' and 'ticker' in event:
                        ticker = event['ticker']
                        stock_counts[ticker] = stock_counts.get(ticker, 0) + 1
                except:
                    continue
        
        # Sort by count
        sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'ticker': ticker, 'count': count} for ticker, count in sorted_stocks[:limit]]
