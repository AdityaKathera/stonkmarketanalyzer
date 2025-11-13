"""Comprehensive Analytics System for Stonk Market Analyzer"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import time
import psutil
from typing import Dict, List, Any

class ComprehensiveAnalytics:
    """Complete analytics system with all admin features"""
    
    def __init__(self):
        # Use relative path from backend directory
        self.analytics_dir = Path(__file__).parent / 'analytics_data'
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory tracking
        self.recent_activity = []
        self.response_times = []
        self.recent_errors = []
        self.api_calls = defaultdict(int)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Limits
        self.max_recent = 200
        self.max_response_times = 2000
        self.max_errors = 100
    
    def track_event(self, event_data: Dict[str, Any]) -> bool:
        """Track any analytics event with enriched data"""
        try:
            # Enrich event data
            event_data['server_timestamp'] = datetime.now().isoformat()
            
            # Add to daily file
            daily_file = self.analytics_dir / f"analytics_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
            with open(daily_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
            
            # Add to recent activity with better formatting
            if event_data.get('event') not in ['page_hidden', 'page_visible', 'heartbeat']:
                activity_item = self._format_activity(event_data)
                self.recent_activity.append(activity_item)
                if len(self.recent_activity) > self.max_recent:
                    self.recent_activity.pop(0)
            
            return True
        except Exception as e:
            print(f"Analytics tracking error: {e}")
            return False
    
    def _format_activity(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format event for activity feed with meaningful descriptions"""
        event_type = event.get('event', 'unknown')
        
        descriptions = {
            'stock_analysis': f"📊 Analyzed {event.get('ticker', 'stock')} - {event.get('step', 'research')}",
            'chat_query': f"💬 Chat: {event.get('query', 'query')[:50]}...",
            'stock_comparison': f"⚖️ Compared {event.get('tickers', 'stocks')}",
            'watchlist_add': f"⭐ Added {event.get('ticker', 'stock')} to watchlist",
            'watchlist_remove': f"❌ Removed {event.get('ticker', 'stock')} from watchlist",
            'research_step': f"🔍 Research step: {event.get('step', 'unknown')}",
            'error': f"⚠️ Error: {event.get('message', 'unknown error')}",
        }
        
        return {
            'description': descriptions.get(event_type, f"📌 {event_type}"),
            'timestamp': event.get('server_timestamp', event.get('timestamp')),
            'userId': event.get('userId', 'anonymous'),
            'details': event
        }
    
    def track_api_call(self, endpoint: str, duration_ms: float, status_code: int = 200):
        """Track API call with performance metrics"""
        self.api_calls[endpoint] += 1
        
        self.response_times.append({
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)
        
        # Track slow queries
        if duration_ms > 2000:  # Slower than 2 seconds
            self.track_error('slow_query', f"{endpoint} took {duration_ms}ms")
    
    def track_error(self, error_type: str, message: str, stack_trace: str = None):
        """Track errors with context"""
        self.recent_errors.append({
            'type': error_type,
            'message': message,
            'stack_trace': stack_trace,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.recent_errors) > self.max_errors:
            self.recent_errors.pop(0)
    
    def track_cache(self, hit: bool):
        """Track cache hit/miss"""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        """Get formatted recent activity"""
        return self.recent_activity[-limit:][::-1]
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if not self.response_times:
            return {
                'avg_response_time': 0,
                'min_response_time': 0,
                'max_response_time': 0,
                'total_requests': 0,
                'slow_queries': 0,
                'by_endpoint': {}
            }
        
        times = [r['duration_ms'] for r in self.response_times]
        slow_queries = len([t for t in times if t > 2000])
        
        # Group by endpoint
        by_endpoint = defaultdict(list)
        for r in self.response_times:
            by_endpoint[r['endpoint']].append(r['duration_ms'])
        
        endpoint_stats = {
            endpoint: {
                'avg': sum(times) / len(times),
                'count': len(times),
                'max': max(times)
            }
            for endpoint, times in by_endpoint.items()
        }
        
        return {
            'avg_response_time': sum(times) / len(times),
            'min_response_time': min(times),
            'max_response_time': max(times),
            'total_requests': len(times),
            'slow_queries': slow_queries,
            'by_endpoint': endpoint_stats
        }
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2),
            'total': total
        }
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent errors"""
        return self.recent_errors[-limit:][::-1]
    
    def get_revenue_metrics(self, date: str = None) -> Dict:
        """Calculate revenue/usage metrics"""
        stats = self.get_daily_stats(date)
        
        # Estimate API costs (example: $0.001 per call)
        api_cost_per_call = 0.001
        total_api_calls = sum(self.api_calls.values())
        
        return {
            'total_api_calls': total_api_calls,
            'estimated_cost': round(total_api_calls * api_cost_per_call, 2),
            'calls_by_endpoint': dict(self.api_calls),
            'avg_calls_per_user': round(total_api_calls / max(stats['unique_users'], 1), 2)
        }
    
    def get_peak_usage_hours(self, date: str = None) -> List[Dict]:
        """Get peak usage hours"""
        hourly = self.get_hourly_stats(date)
        sorted_hours = sorted(hourly, key=lambda x: x['events'], reverse=True)
        return sorted_hours[:5]  # Top 5 peak hours
    
    def get_feature_usage(self, date: str = None) -> Dict:
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
                    event_type = event.get('event', 'unknown')
                    features[event_type] += 1
                except:
                    continue
        
        return dict(features)
    
    def get_user_behavior(self, date: str = None) -> Dict:
        """Analyze user behavior patterns"""
        features = self.get_feature_usage(date)
        
        # Categorize features
        guided = features.get('stock_analysis', 0) + features.get('research_step', 0)
        chat = features.get('chat_query', 0)
        compare = features.get('stock_comparison', 0)
        
        total = guided + chat + compare
        
        return {
            'guided_mode': {'count': guided, 'percentage': round(guided/total*100, 1) if total > 0 else 0},
            'chat_mode': {'count': chat, 'percentage': round(chat/total*100, 1) if total > 0 else 0},
            'compare_mode': {'count': compare, 'percentage': round(compare/total*100, 1) if total > 0 else 0},
            'total_interactions': total
        }
    
    def get_system_health(self) -> Dict:
        """Get system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning'
            }
        except:
            return {'status': 'unknown'}
    
    def get_daily_stats(self, date: str = None) -> Dict:
        """Get comprehensive daily statistics"""
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
        event_counts = defaultdict(int)
        
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
                    event_counts[event_name] += 1
                except:
                    continue
        
        return {
            'date': date,
            'total_events': len(events),
            'unique_users': len(users),
            'unique_sessions': len(sessions),
            'events': dict(event_counts)
        }
    
    def get_hourly_stats(self, date: str = None) -> List[Dict]:
        """Get hourly breakdown"""
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
    
    def get_popular_stocks(self, date: str = None, limit: int = 10) -> List[Dict]:
        """Get most analyzed stocks"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return []
        
        stock_counts = defaultdict(int)
        
        # Events that involve stock analysis
        stock_events = [
            'stock_search', 'stock_analysis', 'research_fundamentals', 
            'research_news', 'research_technical', 'research_overview',
            'chat_query', 'stock_comparison'
        ]
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    event_type = event.get('event', '')
                    ticker = event.get('ticker', '')
                    
                    # Count any stock-related event with a ticker
                    if event_type in stock_events and ticker:
                        # Handle comparison events (ticker format: "AAPL,TSLA")
                        if ',' in ticker:
                            for t in ticker.split(','):
                                t = t.strip()
                                if t:
                                    stock_counts[t] += 1
                        else:
                            stock_counts[ticker] += 1
                except:
                    continue
        
        sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'ticker': ticker, 'count': count} for ticker, count in sorted_stocks[:limit]]
    
    def get_weekly_trend(self, days: int = 7) -> List[Dict]:
        """Get weekly trend data"""
        trend = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            stats = self.get_daily_stats(date)
            trend.append({
                'date': date,
                'users': stats['unique_users'],
                'sessions': stats['unique_sessions'],
                'events': stats['total_events']
            })
        
        return trend[::-1]  # Oldest first
    
    def export_csv(self, date: str = None) -> str:
        """Export to CSV"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        file_path = self.analytics_dir / f"analytics_{date}.jsonl"
        
        if not file_path.exists():
            return "date,event,userId,sessionId,timestamp,ticker\n"
        
        csv_lines = ["date,event,userId,sessionId,timestamp,ticker"]
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    csv_lines.append(
                        f"{date},"
                        f"{event.get('event', '')},"
                        f"{event.get('userId', '')},"
                        f"{event.get('sessionId', '')},"
                        f"{event.get('timestamp', '')},"
                        f"{event.get('ticker', '')}"
                    )
                except:
                    continue
        
        return '\n'.join(csv_lines)
    
    def get_stats(self, date: str = None) -> Dict:
        """Alias for get_daily_stats for backward compatibility"""
        return self.get_daily_stats(date)
    
    def get_performance_stats(self) -> Dict:
        """Alias for get_performance_metrics"""
        return self.get_performance_metrics()
    
    def get_user_retention(self, days: int = 7) -> Dict:
        """Calculate user retention over specified days"""
        retention_data = []
        today = datetime.now().date()
        
        for i in range(days):
            day = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            stats = self.get_daily_stats(day)
            retention_data.append({
                'date': day,
                'users': stats.get('unique_users', 0),
                'sessions': stats.get('unique_sessions', 0),
                'returning_users': 0  # Would need user tracking to calculate properly
            })
        
        return {
            'days': days,
            'data': retention_data[::-1],  # Oldest first
            'total_users': sum(d['users'] for d in retention_data)
        }

# Global instance
comprehensive_analytics = ComprehensiveAnalytics()
