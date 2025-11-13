"""
Authentication and User Management Service
Handles user registration, login, JWT tokens, and session management
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import sqlite3
import secrets

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_hex(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days (default)
JWT_EXPIRATION_HOURS_EXTENDED = 24 * 30  # 30 days (remember me)

# Database setup
DB_PATH = 'users.db'

def init_db():
    """Initialize the user database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            email_verified BOOLEAN DEFAULT 1,
            google_id TEXT,
            auth_provider TEXT DEFAULT 'email',
            primary_auth_method TEXT DEFAULT 'email'
        )
    ''')
    
    # Add new columns to existing tables (migration)
    try:
        c.execute('ALTER TABLE users ADD COLUMN google_id TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute('ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT "email"')
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute('ALTER TABLE users ADD COLUMN primary_auth_method TEXT DEFAULT "email"')
    except sqlite3.OperationalError:
        pass
    
    # Portfolio table
    c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            shares REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, ticker, purchase_date)
        )
    ''')
    
    # Watchlist table
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, ticker)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, email, remember_me=False):
    """Generate a JWT token for a user"""
    expiration_hours = JWT_EXPIRATION_HOURS_EXTENDED if remember_me else JWT_EXPIRATION_HOURS
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_email(email):
    """Get user by email"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(email, password, name=None):
    """Create a new user"""
    password_hash = hash_password(password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (email, password_hash, name)
            VALUES (?, ?, ?)
        ''', (email, password_hash, name))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def update_last_login(user_id):
    """Update user's last login timestamp"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated_function

def update_user_name(user_id, name):
    """Update user's name"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def update_user_password(user_id, new_password):
    """Update user's password"""
    try:
        password_hash = hash_password(new_password)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_user_by_google_id(google_id):
    """Get user by Google ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE google_id = ?', (google_id,))
    user = c.fetchone()
    conn.close()
    return user

def link_google_account(user_id, google_id):
    """Link Google account to existing user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if Google ID is already linked to another account
        existing = get_user_by_google_id(google_id)
        if existing and existing[0] != user_id:
            conn.close()
            return False, "This Google account is already linked to another user"
        
        # Update auth_provider to 'both' if currently 'email'
        c.execute('SELECT auth_provider FROM users WHERE id = ?', (user_id,))
        current_provider = c.fetchone()[0]
        
        new_provider = 'both' if current_provider == 'email' else 'google'
        
        c.execute('''
            UPDATE users 
            SET google_id = ?, auth_provider = ?
            WHERE id = ?
        ''', (google_id, new_provider, user_id))
        
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def unlink_google_account(user_id):
    """Unlink Google account from user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if user has password (can't unlink if Google is only method)
        c.execute('SELECT password_hash, auth_provider FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return False, "User not found"
        
        password_hash, auth_provider = result
        
        # If auth_provider is 'google', user must have a password first
        if auth_provider == 'google':
            conn.close()
            return False, "Cannot unlink Google account. Please set a password first."
        
        # Update to remove Google ID and set provider to 'email'
        c.execute('''
            UPDATE users 
            SET google_id = NULL, auth_provider = 'email', primary_auth_method = 'email'
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def get_linked_accounts(user_id):
    """Get list of linked authentication providers"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT google_id, auth_provider, primary_auth_method FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return []
    
    google_id, auth_provider, primary_auth_method = result
    
    linked = []
    
    # Email/password is always available if auth_provider includes it
    if auth_provider in ['email', 'both']:
        linked.append({
            'provider': 'email',
            'is_primary': primary_auth_method == 'email',
            'linked_at': None  # Could add timestamp if needed
        })
    
    # Google account
    if google_id:
        linked.append({
            'provider': 'google',
            'is_primary': primary_auth_method == 'google',
            'google_id': google_id,
            'linked_at': None
        })
    
    return linked

def set_primary_auth_method(user_id, method):
    """Set primary authentication method"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verify the method is actually linked
        c.execute('SELECT auth_provider, google_id FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return False, "User not found"
        
        auth_provider, google_id = result
        
        # Validate the method is available
        if method == 'google' and not google_id:
            conn.close()
            return False, "Google account is not linked"
        
        if method == 'email' and auth_provider not in ['email', 'both']:
            conn.close()
            return False, "Email authentication is not available"
        
        c.execute('UPDATE users SET primary_auth_method = ? WHERE id = ?', (method, user_id))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)
