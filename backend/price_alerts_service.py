"""
Price Alerts Service
Manages price alerts and notifications
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

class PriceAlertsService:
    """Manage price alerts for users"""
    
    def __init__(self, db_path='stonk_market.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize alerts table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                target_price REAL,
                percentage_change REAL,
                condition TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                triggered BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_alert(self, user_id: int, ticker: str, alert_type: str,
                    target_price: float = None, percentage_change: float = None,
                    condition: str = 'above') -> Optional[int]:
        """
        Create a new price alert
        
        Args:
            user_id: User ID
            ticker: Stock symbol
            alert_type: 'price' or 'percentage'
            target_price: Target price (for price alerts)
            percentage_change: Percentage change (for percentage alerts)
            condition: 'above', 'below', 'up', 'down'
        
        Returns:
            Alert ID or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_alerts 
                (user_id, ticker, alert_type, target_price, percentage_change, condition)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, ticker.upper(), alert_type, target_price, percentage_change, condition))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created alert {alert_id} for user {user_id}: {ticker} {condition} {target_price or percentage_change}")
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None
    
    def get_user_alerts(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all alerts for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM price_alerts 
                WHERE user_id = ?
            '''
            
            if active_only:
                query += ' AND is_active = 1 AND triggered = 0'
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, (user_id,))
            alerts = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return []
    
    def delete_alert(self, alert_id: int, user_id: int) -> bool:
        """Delete an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM price_alerts 
                WHERE id = ? AND user_id = ?
            ''', (alert_id, user_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting alert: {str(e)}")
            return False
    
    def check_alerts(self, ticker: str, current_price: float) -> List[Dict]:
        """
        Check if any alerts should be triggered for a ticker
        
        Args:
            ticker: Stock symbol
            current_price: Current stock price
            
        Returns:
            List of triggered alerts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get active alerts for this ticker
            cursor.execute('''
                SELECT * FROM price_alerts 
                WHERE ticker = ? AND is_active = 1 AND triggered = 0
            ''', (ticker.upper(),))
            
            alerts = [dict(row) for row in cursor.fetchall()]
            triggered_alerts = []
            
            for alert in alerts:
                should_trigger = False
                
                if alert['alert_type'] == 'price':
                    if alert['condition'] == 'above' and current_price >= alert['target_price']:
                        should_trigger = True
                    elif alert['condition'] == 'below' and current_price <= alert['target_price']:
                        should_trigger = True
                
                if should_trigger:
                    # Mark as triggered
                    cursor.execute('''
                        UPDATE price_alerts 
                        SET triggered = 1, triggered_at = ? 
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), alert['id']))
                    
                    triggered_alerts.append(alert)
            
            conn.commit()
            conn.close()
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            return []
    
    def send_alert_notification(self, alert: Dict, current_price: float, user_email: str):
        """Send email notification for triggered alert"""
        try:
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            if not smtp_user or not smtp_password:
                logger.warning("SMTP credentials not configured")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = user_email
            msg['Subject'] = f"🚨 Price Alert: {alert['ticker']} reached ${current_price}"
            
            body = f"""
            Your price alert has been triggered!
            
            Stock: {alert['ticker']}
            Current Price: ${current_price}
            Alert Condition: {alert['condition']} ${alert['target_price']}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            View your portfolio: https://stonkmarketanalyzer.com
            
            ---
            Stonk Market Analyzer
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Sent alert notification to {user_email} for {alert['ticker']}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")


# Global instance
price_alerts_service = PriceAlertsService()
