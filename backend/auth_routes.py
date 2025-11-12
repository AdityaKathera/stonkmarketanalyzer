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
    
    # Generate token
    token = generate_token(user_id, email)
    
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
