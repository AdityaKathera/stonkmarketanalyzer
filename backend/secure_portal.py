"""
Secure Admin Portal for Stonk Market Analyzer
High-security implementation with JWT authentication, rate limiting, and brute force protection
"""

import jwt
import hashlib
import secrets
import os
import time
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from collections import defaultdict

# Generate secure secret key (store this in .env in production)
SECRET_KEY = os.getenv('PORTAL_SECRET_KEY', secrets.token_urlsafe(64))
PORTAL_PATH = os.getenv('PORTAL_PATH', 'x9k2m7p4q8w1')  # Obscure path
PORTAL_USERNAME = os.getenv('PORTAL_USERNAME', 'sentinel_' + secrets.token_hex(4))
PORTAL_PASSWORD_HASH = os.getenv('PORTAL_PASSWORD_HASH', '')  # Will be set on first run

# Security: Rate limiting and brute force protection
login_attempts = defaultdict(list)  # IP -> list of attempt timestamps
locked_ips = {}  # IP -> lock expiry timestamp
MAX_ATTEMPTS = 3  # Max failed attempts before lockout
LOCKOUT_DURATION = 900  # 15 minutes lockout
RATE_LIMIT_WINDOW = 60  # 1 minute window for rate limiting
MAX_REQUESTS_PER_MINUTE = 10  # Max requests per minute per IP

# Optional: IP Whitelist (set in .env as comma-separated IPs)
ALLOWED_IPS = os.getenv('PORTAL_ALLOWED_IPS', '').split(',') if os.getenv('PORTAL_ALLOWED_IPS') else []

def hash_password(password):
    """Hash password with SHA-256 and salt"""
    salt = os.getenv('PORTAL_SALT', secrets.token_hex(32))
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password, password_hash):
    """Verify password against hash"""
    # Password hash format: salt:hash
    if ':' in password_hash:
        stored_salt, stored_hash = password_hash.split(':', 1)
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), stored_salt.encode(), 100000).hex()
        return computed_hash == stored_hash
    else:
        # Fallback for old format
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

def get_client_ip():
    """Get real client IP (handles proxies)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def is_ip_locked(ip):
    """Check if IP is currently locked out"""
    if ip in locked_ips:
        if time.time() < locked_ips[ip]:
            return True
        else:
            # Lock expired, remove it
            del locked_ips[ip]
            if ip in login_attempts:
                del login_attempts[ip]
    return False

def record_failed_attempt(ip):
    """Record a failed login attempt"""
    current_time = time.time()
    
    # Clean old attempts (older than lockout duration)
    login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < LOCKOUT_DURATION]
    
    # Add new attempt
    login_attempts[ip].append(current_time)
    
    # Check if should lock
    if len(login_attempts[ip]) >= MAX_ATTEMPTS:
        locked_ips[ip] = current_time + LOCKOUT_DURATION
        return True
    
    return False

def check_rate_limit(ip):
    """Check if IP is rate limited"""
    current_time = time.time()
    
    # Get recent requests
    if ip not in login_attempts:
        login_attempts[ip] = []
    
    recent_requests = [t for t in login_attempts[ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(recent_requests) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    return True

def check_ip_whitelist(ip):
    """Check if IP is in whitelist (if whitelist is enabled)"""
    if not ALLOWED_IPS or ALLOWED_IPS == ['']:
        return True  # Whitelist disabled
    return ip in ALLOWED_IPS

def require_auth(f):
    """Decorator to require authentication with security checks"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = get_client_ip()
        
        # Check IP whitelist
        if not check_ip_whitelist(ip):
            return jsonify({'error': 'Access denied from your IP'}), 403
        
        # Check if IP is locked
        if is_ip_locked(ip):
            remaining = int(locked_ips[ip] - time.time())
            return jsonify({
                'error': 'Too many failed attempts. Account locked.',
                'retry_after': remaining
            }), 429
        
        # Check rate limit
        if not check_rate_limit(ip):
            return jsonify({'error': 'Too many requests. Please slow down.'}), 429
        
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
        """Secure login endpoint with brute force protection"""
        ip = get_client_ip()
        
        # Check IP whitelist
        if not check_ip_whitelist(ip):
            return jsonify({'error': 'Access denied from your IP'}), 403
        
        # Check if IP is locked
        if is_ip_locked(ip):
            remaining = int(locked_ips[ip] - time.time())
            return jsonify({
                'error': 'Too many failed attempts. Account locked.',
                'retry_after': remaining,
                'locked_until': datetime.fromtimestamp(locked_ips[ip]).isoformat()
            }), 429
        
        # Check rate limit
        if not check_rate_limit(ip):
            return jsonify({'error': 'Too many requests. Please slow down.'}), 429
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Add delay to slow down brute force (timing attack mitigation)
        time.sleep(0.5)
        
        # Verify credentials
        if username != PORTAL_USERNAME:
            record_failed_attempt(ip)
            attempts_left = MAX_ATTEMPTS - len(login_attempts[ip])
            return jsonify({
                'error': 'Invalid credentials',
                'attempts_left': max(0, attempts_left)
            }), 401
        
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
            is_locked = record_failed_attempt(ip)
            attempts_left = MAX_ATTEMPTS - len(login_attempts[ip])
            
            if is_locked:
                return jsonify({
                    'error': 'Too many failed attempts. Account locked for 15 minutes.',
                    'locked_until': datetime.fromtimestamp(locked_ips[ip]).isoformat()
                }), 429
            
            return jsonify({
                'error': 'Invalid credentials',
                'attempts_left': max(0, attempts_left)
            }), 401
        
        # Successful login - clear failed attempts
        if ip in login_attempts:
            del login_attempts[ip]
        if ip in locked_ips:
            del locked_ips[ip]
        
        # Generate token
        token = generate_token(username)
        
        # Log successful login
        print(f"[SECURITY] Successful login from IP: {ip} at {datetime.now().isoformat()}")
        
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
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/activity', methods=['GET'])
    @require_auth
    def portal_recent_activity():
        """Get recent activity feed"""
        try:
            limit = int(request.args.get('limit', 50))
            activity = analytics_service.get_recent_activity(limit)
            return jsonify({'activity': activity}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/performance', methods=['GET'])
    @require_auth
    def portal_performance():
        """Get performance statistics"""
        try:
            stats = analytics_service.get_performance_stats()
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/errors', methods=['GET'])
    @require_auth
    def portal_errors():
        """Get recent errors"""
        try:
            limit = int(request.args.get('limit', 20))
            errors = analytics_service.get_recent_errors(limit)
            return jsonify({'errors': errors}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/hourly', methods=['GET'])
    @require_auth
    def portal_hourly():
        """Get hourly breakdown"""
        try:
            date = request.args.get('date')
            hourly = analytics_service.get_hourly_stats(date)
            return jsonify({'hourly': hourly}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/features', methods=['GET'])
    @require_auth
    def portal_features():
        """Get feature usage"""
        try:
            date = request.args.get('date')
            features = analytics_service.get_feature_usage(date)
            return jsonify({'features': features}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/retention', methods=['GET'])
    @require_auth
    def portal_retention():
        """Get user retention data"""
        try:
            days = int(request.args.get('days', 7))
            retention = analytics_service.get_user_retention(days)
            return jsonify({'retention': retention}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/analytics/export', methods=['GET'])
    @require_auth
    def portal_export():
        """Export analytics as CSV"""
        try:
            date = request.args.get('date')
            csv_data = analytics_service.export_to_csv(date)
            
            from flask import Response
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=analytics_{date or "today"}.csv'}
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route(f'/api/{PORTAL_PATH}/cache/stats', methods=['GET'])
    @require_auth
    def portal_cache_stats():
        """Get cache statistics"""
        try:
            stats = analytics_service.get_cache_stats()
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return PORTAL_PATH, PORTAL_USERNAME
