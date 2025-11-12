"""
Password Reset Service
Handles password reset tokens and email notifications
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

DB_PATH = 'users.db'

class PasswordResetService:
    """Handle password reset functionality"""
    
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name='us-east-1')
        self.from_email = 'password-reset@stonkmarketanalyzer.com'
        self.frontend_url = os.getenv('FRONTEND_URL', 'https://stonkmarketanalyzer.com')
        self.init_db()
    
    def init_db(self):
        """Initialize password reset tokens table"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def generate_reset_token(self, email):
        """Generate a password reset token for a user"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT id, name FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return None, "User not found"
        
        user_id, name = user
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Store token
        c.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, token, expires_at))
        
        conn.commit()
        conn.close()
        
        # Send email
        self.send_reset_email(email, name, token)
        
        return token, None
    
    def send_reset_email(self, email, name, token):
        """Send password reset email"""
        reset_link = f"{self.frontend_url}/reset-password?token={token}"
        
        subject = "Reset Your Password - Stonk Market Analyzer"
        
        body_text = f"""
Hi {name or 'there'},

You requested to reset your password for Stonk Market Analyzer.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Stonk Market Analyzer Team
"""
        
        body_html = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }}
        .button {{
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
            font-size: 14px;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔐 Password Reset</h1>
        <p>Stonk Market Analyzer</p>
    </div>
    
    <div class="content">
        <p>Hi {name or 'there'},</p>
        
        <p>You requested to reset your password for your Stonk Market Analyzer account.</p>
        
        <p>Click the button below to reset your password:</p>
        
        <center>
            <a href="{reset_link}" class="button">Reset Password</a>
        </center>
        
        <div class="warning">
            <strong>⏰ This link expires in 1 hour</strong>
        </div>
        
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
        
        <div class="footer">
            <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            <p>For security reasons, this link can only be used once.</p>
            <p><strong>Stonk Market Analyzer</strong><br>
            <a href="{self.frontend_url}">{self.frontend_url}</a></p>
        </div>
    </div>
</body>
</html>
"""
        
        try:
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                        'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                    }
                }
            )
            print(f"[PASSWORD_RESET] Email sent to {email}")
            return True
        except ClientError as e:
            print(f"[PASSWORD_RESET] Error sending email: {e.response['Error']['Message']}")
            return False
    
    def verify_reset_token(self, token):
        """Verify if a reset token is valid"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT user_id, expires_at, used 
            FROM password_reset_tokens 
            WHERE token = ?
        ''', (token,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None, "Invalid token"
        
        user_id, expires_at, used = result
        
        if used:
            return None, "Token already used"
        
        expires_at = datetime.fromisoformat(expires_at)
        if datetime.utcnow() > expires_at:
            return None, "Token expired"
        
        return user_id, None
    
    def reset_password(self, token, new_password):
        """Reset password using a valid token"""
        from auth_service import hash_password
        
        user_id, error = self.verify_reset_token(token)
        
        if error:
            return False, error
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Update password
        password_hash = hash_password(new_password)
        c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        
        # Mark token as used
        c.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
        
        conn.commit()
        conn.close()
        
        return True, None
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens (run periodically)"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            DELETE FROM password_reset_tokens 
            WHERE expires_at < datetime('now') OR used = 1
        ''')
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        return deleted
