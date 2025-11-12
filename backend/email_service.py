"""Email notification service using AWS SES"""

import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime

class EmailService:
    """Send email notifications via AWS SES"""
    
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name='us-east-1')
        self.from_email = os.getenv('ADMIN_EMAIL', 'sentinel_65d3d147@stonkmarketanalyzer.com')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'sentinel_65d3d147@stonkmarketanalyzer.com')
    
    def send_email(self, subject, body_text, body_html=None, to_email=None):
        """Send an email via SES"""
        if to_email is None:
            to_email = self.admin_email
        
        try:
            body_data = {'Text': {'Data': body_text, 'Charset': 'UTF-8'}}
            
            if body_html:
                body_data['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
            
            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': body_data
                }
            )
            
            print(f"[EMAIL] Sent: {subject} to {to_email}")
            return True
            
        except ClientError as e:
            print(f"[EMAIL] Error: {e.response['Error']['Message']}")
            return False
    
    def send_daily_report(self, stats):
        """Send daily analytics report"""
        subject = f"📊 Daily Report - {stats['date']}"
        
        body_text = f"""
Stonk Market Analyzer - Daily Report
=====================================

Date: {stats['date']}

📈 METRICS
----------
Total Events: {stats['total_events']}
Unique Users: {stats['unique_users']}
Unique Sessions: {stats['unique_sessions']}

🔥 TOP STOCKS
-------------
"""
        
        for i, stock in enumerate(stats.get('popular_stocks', [])[:10], 1):
            body_text += f"{i}. {stock['ticker']}: {stock['count']} analyses\n"
        
        body_text += f"""

🔗 Admin Portal: https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html

---
Stonk Market Analyzer
"""
        
        body_html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .stock-list {{ list-style: none; padding: 0; }}
        .stock-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Daily Report</h1>
        <p>{stats['date']}</p>
    </div>
    
    <h2>📈 Metrics</h2>
    <div class="metric">
        <div>Total Events</div>
        <div class="metric-value">{stats['total_events']}</div>
    </div>
    <div class="metric">
        <div>Unique Users</div>
        <div class="metric-value">{stats['unique_users']}</div>
    </div>
    <div class="metric">
        <div>Unique Sessions</div>
        <div class="metric-value">{stats['unique_sessions']}</div>
    </div>
    
    <h2>🔥 Top Stocks</h2>
    <ul class="stock-list">
"""
        
        for i, stock in enumerate(stats.get('popular_stocks', [])[:10], 1):
            body_html += f'<li class="stock-item">{i}. <strong>{stock["ticker"]}</strong>: {stock["count"]} analyses</li>'
        
        body_html += """
    </ul>
    
    <div class="footer">
        <p><a href="https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html">View Admin Portal</a></p>
        <p>Stonk Market Analyzer</p>
    </div>
</body>
</html>
"""
        
        return self.send_email(subject, body_text, body_html)
    
    def send_alert(self, alert_type, message, details=None):
        """Send alert notification"""
        subject = f"🚨 Alert: {alert_type}"
        
        body_text = f"""
Stonk Market Analyzer - Alert
==============================

Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message: {message}
"""
        
        if details:
            body_text += f"\nDetails:\n{details}\n"
        
        body_text += """
---
Check admin portal for more information:
https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html
"""
        
        return self.send_email(subject, body_text)
    
    def send_error_notification(self, error_message, stack_trace=None):
        """Send error notification"""
        subject = "❌ Error Detected"
        
        body_text = f"""
Stonk Market Analyzer - Error Notification
===========================================

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error: {error_message}
"""
        
        if stack_trace:
            body_text += f"\nStack Trace:\n{stack_trace}\n"
        
        body_text += """
---
Check logs for more details:
ssh ec2-user@100.27.225.93
sudo journalctl -u stonkmarketanalyzer -n 100
"""
        
        return self.send_email(subject, body_text)

