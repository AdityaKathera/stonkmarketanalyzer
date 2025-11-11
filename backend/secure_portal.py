"""
Secure Admin Portal for Stonk Market Analyzer
High-security implementation with JWT authentication
"""

import jwt
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Generate secure secret key (store this in .env in production)
SECRET_KEY = os.getenv('PORTAL_SECRET_KEY', secrets.token_urlsafe(64))
PORTAL_PATH = os.getenv('PORTAL_PATH', 'x9k2m7p4q8w1')  # Obscure path
PORTAL_USERNAME = os.getenv('PORTAL_USERNAME', 'sentinel_' + secrets.token_hex(4))
PORTAL_PASSWORD_HASH = os.getenv('PORTAL_PASSWORD_HASH', '')  # Will be set on first run

def hash_password(password):
    """Hash password with SHA-256 and salt"""
    salt = os.getenv('PORTAL_SALT', secrets.token_hex(32))
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def generate_token(username):
    """Generate JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=2),  # Token expires in 2 hours
        'iat': datetime.utcnow(),
        'jti': secrets.token_hex(16)  # Unique token ID
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No authorization token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def setup_portal_routes(app, analytics_service):
    """Setup secure portal routes"""
    
    @app.route(f'/api/{PORTAL_PATH}/auth', methods=['POST'])
    def portal_login():
        """Secure login endpoint"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Verify credentials
        if username != PORTAL_USERNAME:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not PORTAL_PASSWORD_HASH:
            # First time setup - set password
            password_hash = hash_password(password)
            # In production, save this to .env
            return jsonify({
                'message': 'First time setup',
                'password_hash': password_hash,
                'note': 'Save this hash to PORTAL_PASSWORD_HASH in .env'
            }), 200
        
        if not verify_password(password, PORTAL_PASSWORD_HASH):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(username)
        
        return jsonify({
            'token': token,
            'expires_in': 7200  # 2 hours
        }), 200
    
    @app.route(f'/api/{PORTAL_PATH}/verify', methods=['GET'])
    @require_auth
    def verify_portal_token():
        """Verify token is still valid"""
        return jsonify({'valid': True}), 200
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/overview', methods=['GET'])
    @require_auth
    def portal_analytics_overview():
        """Get analytics overview"""
        try:
            # Get stats for today
            today_stats = analytics_service.get_stats()
            
            # Get stats for last 7 days
            from datetime import date, timedelta
            weekly_stats = []
            for i in range(7):
                day = (date.today() - timedelta(days=i)).strftime('%Y-%m-%d')
                stats = analytics_service.get_stats(day)
                weekly_stats.append({
                    'date': day,
                    'users': stats['unique_users'],
                    'sessions': stats['unique_sessions'],
                    'events': stats['total_events']
                })
            
            # Get popular stocks
            popular_stocks = analytics_service.get_popular_stocks(limit=20)
            
            return jsonify({
                'today': today_stats,
                'weekly': weekly_stats,
                'popular_stocks': popular_stocks
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/raw', methods=['GET'])
    @require_auth
    def portal_analytics_raw():
        """Get raw analytics data"""
        try:
            date_param = request.args.get('date')
            stats = analytics_service.get_stats(date_param)
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/system/health', methods=['GET'])
    @require_auth
    def portal_system_health():
        """Get system health information"""
        try:
            import psutil
            
            return jsonify({
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent': psutil.disk_usage('/').percent
                }
            }), 200
        except ImportError:
            return jsonify({'error': 'psutil not installed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return PORTAL_PATH, PORTAL_USERNAME
