"""Analytics tracking and storage for Stonk Market Analyzer"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import time

class AnalyticsService:
    """Enhanced analytics with real-time tracking and insights"""
    
    def __init__(self):
        self.analytics_dir = Path('/opt/stonkmarketanalyzer/analytics')
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        self.daily_file = self.analytics_dir / f"analytics_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        # Real-time activity tracking (in-memory)
        self.recent_activity = []  # Last 100 events
        self.max_recent = 100
        
        # Performance tracking
        self.response_times = []  # Last 1000 response times
        self.max_response_times = 1000
        
        # Error tracking
        self.recent_errors = []  # Last 50 errors
        self.max_errors = 50
    
    def track_event(self, event_data):
        """Store analytics event"""
        try:
            # Add server timestamp
            event_data['server_timestamp'] = datetime.now().isoformat()
            
            # Append to daily file
            with open(self.daily_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
            
            # Add to recent activity (in-memory)
            self.recent_activity.append(event_data)
            if len(self.recent_activity) > self.max_recent:
                self.recent_activity.pop(0)
            
            return True
        except Exception as e:
            print(f"Analytics error: {e}")
            return False
    
    def track_response_time(self, endpoint, duration_ms):
        """Track API response time"""
        self.response_times.append({
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'timestamp': time.time()
        })
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)
    
    def track_error(self, error_type, error_message, stack_trace=None):
        """Track error occurrence"""
        self.recent_errors.append({
            'type': error_type,
            'message': error_message,
            'stack_trace': stack_trace,
            'timestamp': datetime.now().isoformat()
        })
        if len(self.recent_errors) > self.max_errors:
            self.recent_errors.pop(0)
    
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

    
    def get_recent_activity(self, limit=50):
        """Get recent activity feed"""
        return self.recent_activity[-limit:][::-1]  # Most recent first
    
    def get_performance_stats(self):
        """Get API performance statistics"""
        if not self.response_times:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'total_requests': 0
            }
        
        times = [r['duration_ms'] for r in self.response_times]
        return {
            'avg_response_time': sum(times) / len(times),
            'min_response_time': min(times),
            'max_response_time': max(times),
            'total_requests': len(times),
            'by_endpoint': self._group_by_endpoint()
        }
    
    def _group_by_endpoint(self):
        """Group response times by endpoint"""
        by_endpoint = defaultdict(list)
        for r in self.response_times:
            by_endpoint[r['endpoint']].append(r['duration_ms'])
        
        return {
            endpoint: {
                'avg': sum(times) / len(times),
                'count': len(times)
            }
            for endpoint, times in by_endpoint.items()
        }
    
    def get_recent_errors(self, limit=20):
        """Get recent errors"""
        return self.recent_errors[-limit:][::-1]
    
    def get_hourly_stats(self, date=None):
        """Get hourly breakdown of activity"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return []
        
        hourly = defaultdict(lambda: {'events': 0, 'users': set(), 'sessions': set()})
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    timestamp = event.get('server_timestamp', event.get('timestamp', ''))
                    if timestamp:
                        hour = timestamp[:13]  # YYYY-MM-DDTHH
                        hourly[hour]['events'] += 1
                        if 'userId' in event:
                            hourly[hour]['users'].add(event['userId'])
                        if 'sessionId' in event:
                            hourly[hour]['sessions'].add(event['sessionId'])
                except:
                    continue
        
        return [
            {
                'hour': hour,
                'events': data['events'],
                'users': len(data['users']),
                'sessions': len(data['sessions'])
            }
            for hour, data in sorted(hourly.items())
        ]
    
    def get_feature_usage(self, date=None):
        """Get feature usage breakdown"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return {}
        
        features = defaultdict(int)
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    feature = event.get('feature', event.get('event', 'unknown'))
                    features[feature] += 1
                except:
                    continue
        
        return dict(features)
    
    def get_user_retention(self, days=7):
        """Get user retention data"""
        retention = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            stats = self.get_stats(date)
            retention.append({
                'date': date,
                'users': stats['unique_users'],
                'sessions': stats['unique_sessions']
            })
        
        return retention[::-1]  # Oldest first
    
    def get_cache_stats(self):
        """Get cache statistics (if cache is available)"""
        try:
            from cache import response_cache
            return {
                'size': response_cache.size(),
                'ttl': response_cache.ttl,
                'hit_rate': getattr(response_cache, 'hit_rate', 0)
            }
        except:
            return {'size': 0, 'ttl': 0, 'hit_rate': 0}
    
    def export_to_csv(self, date=None):
        """Export analytics to CSV format"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return "date,event,userId,sessionId,timestamp\n"
        
        csv_lines = ["date,event,userId,sessionId,timestamp"]
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    csv_lines.append(
                        f"{date},"
                        f"{event.get('event', '')},"
                        f"{event.get('userId', '')},"
                        f"{event.get('sessionId', '')},"
                        f"{event.get('timestamp', '')}"
                    )
                except:
                    continue
        
        return '\n'.join(csv_lines)
