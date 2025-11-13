"""
User Authentication and Portfolio API Routes
Handles sign-up, login, and portfolio management
"""

from flask import Blueprint, request, jsonify
from auth_service import (
    create_user, get_user_by_email, verify_password, generate_token,
    update_last_login, require_auth, get_user_by_id
)
import sqlite3
import os
import secrets

auth_bp = Blueprint('auth', __name__)
DB_PATH = 'users.db'

# Session configuration
SESSION_SECRET = os.getenv('SESSION_SECRET', secrets.token_hex(32))

@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    data = request.json
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    
    # Validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    if '@' not in email:
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Check if user exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user_id = create_user(email, password, name)
    
    if not user_id:
        return jsonify({'error': 'Failed to create user'}), 500
    
    # Generate JWT token
    token = generate_token(user_id, email)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user_id,
            'email': email,
            'name': name
        },
        'message': 'Account created successfully'
    }), 201

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user
    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    user_id, user_email, password_hash, name = user[0], user[1], user[2], user[3]
    
    if not verify_password(password, password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login
    update_last_login(user_id)
    
    # Generate token with remember_me option
    token = generate_token(user_id, email, remember_me)
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'id': user_id,
            'email': email,
            'name': name
        }
    }), 200

@auth_bp.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    user = get_user_by_id(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user[0],
        'email': user[1],
        'name': user[3],
        'created_at': user[4],
        'last_login': user[5]
    }), 200

@auth_bp.route('/api/auth/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile (name)"""
    from auth_service import update_user_name
    
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    success = update_user_name(request.user_id, name)
    
    if not success:
        return jsonify({'error': 'Failed to update profile'}), 500
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'name': name
    }), 200

@auth_bp.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    from auth_service import update_user_password
    
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password are required'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    
    # Verify current password
    user = get_user_by_id(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    password_hash = user[2]
    if not verify_password(current_password, password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    success = update_user_password(request.user_id, new_password)
    
    if not success:
        return jsonify({'error': 'Failed to update password'}), 500
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200

# Portfolio Management Routes

@auth_bp.route('/api/portfolio', methods=['GET'])
@require_auth
def get_portfolio():
    """Get user's portfolio"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM portfolio 
        WHERE user_id = ? 
        ORDER BY ticker ASC
    ''', (request.user_id,))
    
    holdings = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({'holdings': holdings}), 200

@auth_bp.route('/api/portfolio', methods=['POST'])
@require_auth
def add_to_portfolio():
    """Add stock to portfolio"""
    data = request.json
    
    ticker = data.get('ticker', '').upper()
    shares = data.get('shares')
    purchase_price = data.get('purchase_price')
    purchase_date = data.get('purchase_date')
    notes = data.get('notes', '')
    
    if not all([ticker, shares, purchase_price, purchase_date]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO portfolio (user_id, ticker, shares, purchase_price, purchase_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (request.user_id, ticker, shares, purchase_price, purchase_date, notes))
        holding_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'holding_id': holding_id,
            'message': f'{ticker} added to portfolio'
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Holding already exists'}), 409

@auth_bp.route('/api/portfolio/<int:holding_id>', methods=['PUT'])
@require_auth
def update_portfolio_holding(holding_id):
    """Update a portfolio holding"""
    data = request.json
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Verify ownership
    c.execute('SELECT user_id FROM portfolio WHERE id = ?', (holding_id,))
    result = c.fetchone()
    
    if not result or result[0] != request.user_id:
        conn.close()
        return jsonify({'error': 'Holding not found'}), 404
    
    # Update fields
    updates = []
    params = []
    
    if 'shares' in data:
        updates.append('shares = ?')
        params.append(data['shares'])
    if 'purchase_price' in data:
        updates.append('purchase_price = ?')
        params.append(data['purchase_price'])
    if 'notes' in data:
        updates.append('notes = ?')
        params.append(data['notes'])
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(holding_id)
        
        c.execute(f'''
            UPDATE portfolio 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        conn.commit()
    
    conn.close()
    return jsonify({'success': True, 'message': 'Holding updated'}), 200

@auth_bp.route('/api/portfolio/<int:holding_id>', methods=['DELETE'])
@require_auth
def delete_portfolio_holding(holding_id):
    """Delete a portfolio holding"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Verify ownership and delete
    c.execute('DELETE FROM portfolio WHERE id = ? AND user_id = ?', 
              (holding_id, request.user_id))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Holding not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Holding deleted'}), 200

# Enhanced Portfolio Routes with Real-Time Data

@auth_bp.route('/api/portfolio/summary', methods=['GET'])
@require_auth
def get_portfolio_summary():
    """Get portfolio with real-time prices and performance metrics"""
    try:
        from portfolio_service import portfolio_service
        portfolio_data = portfolio_service.get_portfolio_with_metrics(request.user_id)
        return jsonify(portfolio_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/portfolio/allocation', methods=['GET'])
@require_auth
def get_portfolio_allocation():
    """Get portfolio allocation breakdown"""
    try:
        from portfolio_service import portfolio_service
        allocation = portfolio_service.get_portfolio_allocation(request.user_id)
        return jsonify(allocation), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/portfolio/insights', methods=['GET'])
@require_auth
def get_portfolio_insights():
    """Get AI-powered portfolio insights and recommendations"""
    try:
        from portfolio_insights_service import portfolio_insights_service
        insights = portfolio_insights_service.get_portfolio_insights(request.user_id)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Watchlist Routes

@auth_bp.route('/api/watchlist', methods=['GET'])
@require_auth
def get_watchlist():
    """Get user's watchlist"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM watchlist 
        WHERE user_id = ? 
        ORDER BY added_at DESC
    ''', (request.user_id,))
    
    stocks = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify({'watchlist': stocks}), 200

@auth_bp.route('/api/watchlist', methods=['POST'])
@require_auth
def add_to_watchlist():
    """Add stock to watchlist"""
    data = request.json
    
    ticker = data.get('ticker', '').upper()
    notes = data.get('notes', '')
    
    if not ticker:
        return jsonify({'error': 'Ticker is required'}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO watchlist (user_id, ticker, notes)
            VALUES (?, ?, ?)
        ''', (request.user_id, ticker, notes))
        watchlist_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'watchlist_id': watchlist_id,
            'message': f'{ticker} added to watchlist'
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Stock already in watchlist'}), 409

@auth_bp.route('/api/watchlist/<int:watchlist_id>', methods=['DELETE'])
@require_auth
def remove_from_watchlist(watchlist_id):
    """Remove stock from watchlist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM watchlist WHERE id = ? AND user_id = ?', 
              (watchlist_id, request.user_id))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Stock not found in watchlist'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Stock removed from watchlist'}), 200

# Password Reset Routes

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    from password_reset_service import PasswordResetService
    
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    reset_service = PasswordResetService()
    token, error = reset_service.generate_reset_token(email)
    
    # Always return success to prevent email enumeration
    return jsonify({
        'success': True,
        'message': 'If an account exists with that email, a password reset link has been sent.'
    }), 200

@auth_bp.route('/api/auth/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a reset token is valid"""
    from password_reset_service import PasswordResetService
    
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    reset_service = PasswordResetService()
    user_id, error = reset_service.verify_reset_token(token)
    
    if error:
        return jsonify({'error': error, 'valid': False}), 400
    
    return jsonify({'valid': True}), 200

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    from password_reset_service import PasswordResetService
    
    data = request.json
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and password are required'}), 400
    
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    reset_service = PasswordResetService()
    success, error = reset_service.reset_password(token, new_password)
    
    if not success:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Password reset successfully. You can now login with your new password.'
    }), 200

# Google OAuth Routes

@auth_bp.route('/api/auth/google', methods=['POST'])
def google_auth():
    """Authenticate with Google OAuth"""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    from auth_service import get_user_by_google_id
    
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Google token is required'}), 400
    
    try:
        # Verify Google token
        CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            CLIENT_ID
        )
        
        # Get user info from Google
        email = idinfo['email']
        name = idinfo.get('name', '')
        google_id = idinfo['sub']
        
        # Check if Google ID is already linked to an account
        user_by_google = get_user_by_google_id(google_id)
        
        if user_by_google:
            # User has linked Google account - login
            user_id = user_by_google[0]
            update_last_login(user_id)
        else:
            # Check if email exists (for potential linking)
            user_by_email = get_user_by_email(email)
            
            if user_by_email:
                # Email exists but Google not linked - auto-link and login
                user_id = user_by_email[0]
                from auth_service import link_google_account
                success, error = link_google_account(user_id, google_id)
                
                if not success:
                    return jsonify({'error': error}), 400
                
                update_last_login(user_id)
            else:
                # New user - create account with Google
                random_password = secrets.token_urlsafe(32)
                user_id = create_user(email, random_password, name)
                
                if not user_id:
                    return jsonify({'error': 'Failed to create user'}), 500
                
                # Link Google ID to new account
                from auth_service import link_google_account
                link_google_account(user_id, google_id)
        
        # Generate JWT token
        jwt_token = generate_token(user_id, email)
        
        return jsonify({
            'success': True,
            'token': jwt_token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            },
            'message': 'Logged in with Google successfully'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid Google token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Account Linking Routes

@auth_bp.route('/api/auth/linked-accounts', methods=['GET'])
@require_auth
def get_linked_accounts_route():
    """Get list of linked authentication providers"""
    from auth_service import get_linked_accounts
    
    linked = get_linked_accounts(request.user_id)
    
    return jsonify({
        'linked_accounts': linked
    }), 200

@auth_bp.route('/api/auth/link-google', methods=['POST'])
@require_auth
def link_google():
    """Link Google account to current user"""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    from auth_service import link_google_account
    
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Google token is required'}), 400
    
    try:
        # Verify Google token
        CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            CLIENT_ID
        )
        
        google_id = idinfo['sub']
        google_email = idinfo['email']
        
        # Verify the Google email matches the user's email
        user = get_user_by_id(request.user_id)
        if user[1] != google_email:
            return jsonify({
                'error': 'Google account email does not match your account email'
            }), 400
        
        # Link the account
        success, error = link_google_account(request.user_id, google_id)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'success': True,
            'message': 'Google account linked successfully'
        }), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid Google token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/unlink-google', methods=['DELETE'])
@require_auth
def unlink_google():
    """Unlink Google account from current user"""
    from auth_service import unlink_google_account
    
    success, error = unlink_google_account(request.user_id)
    
    if not success:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': 'Google account unlinked successfully'
    }), 200

@auth_bp.route('/api/auth/primary-method', methods=['PUT'])
@require_auth
def set_primary_method():
    """Set primary authentication method"""
    from auth_service import set_primary_auth_method
    
    data = request.json
    method = data.get('method')
    
    if method not in ['email', 'google']:
        return jsonify({'error': 'Invalid authentication method'}), 400
    
    success, error = set_primary_auth_method(request.user_id, method)
    
    if not success:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'success': True,
        'message': f'Primary authentication method set to {method}'
    }), 200

# ============================================================================
# NEWS ENDPOINTS - AI News Summarizer
# ============================================================================

from news_service import get_news_service
from news_summarizer_service import get_summarizer_service

@auth_bp.route('/api/news/stock/<ticker>', methods=['GET'])
@require_auth
def get_stock_news(ticker):
    """
    Get AI-summarized news for a specific stock
    Query params: limit (default: 5)
    """
    try:
        limit = int(request.args.get('limit', 5))
        
        # Get news
        news_service = get_news_service()
        news_items = news_service.get_news_for_stock(ticker.upper(), limit)
        
        # Summarize with AI
        summarizer = get_summarizer_service()
        summarized_news = summarizer.summarize_multiple(news_items, ticker.upper())
        
        return jsonify({
            'ticker': ticker.upper(),
            'news': summarized_news,
            'count': len(summarized_news)
        }), 200
        
    except Exception as e:
        print(f"[API] Error fetching news for {ticker}: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500


@auth_bp.route('/api/news/watchlist', methods=['GET'])
@require_auth
def get_watchlist_news():
    """
    Get AI-summarized news for all stocks in user's watchlist
    Query params: limit_per_stock (default: 3)
    """
    try:
        user_id = request.user_id
        limit_per_stock = int(request.args.get('limit_per_stock', 3))
        
        # Get user's watchlist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticker FROM watchlist 
            WHERE user_id = ? 
            ORDER BY added_at DESC
        ''', (user_id,))
        
        watchlist_tickers = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not watchlist_tickers:
            return jsonify({
                'news': {},
                'message': 'No stocks in watchlist'
            }), 200
        
        # Get news for all watchlist stocks
        news_service = get_news_service()
        summarizer = get_summarizer_service()
        
        all_news = {}
        for ticker in watchlist_tickers[:10]:  # Limit to 10 stocks to avoid rate limits
            news_items = news_service.get_news_for_stock(ticker, limit_per_stock)
            summarized = summarizer.summarize_multiple(news_items, ticker)
            all_news[ticker] = summarized
        
        return jsonify({
            'news': all_news,
            'tickers': watchlist_tickers[:10],
            'count': len(all_news)
        }), 200
        
    except Exception as e:
        print(f"[API] Error fetching watchlist news: {e}")
        return jsonify({'error': 'Failed to fetch watchlist news'}), 500


@auth_bp.route('/api/news/refresh', methods=['POST'])
@require_auth
def refresh_news_cache():
    """
    Clear news cache to force refresh
    """
    try:
        news_service = get_news_service()
        summarizer = get_summarizer_service()
        
        news_service.clear_cache()
        summarizer.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'News cache cleared'
        }), 200
        
    except Exception as e:
        print(f"[API] Error clearing cache: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500
