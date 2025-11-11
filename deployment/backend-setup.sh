#!/bin/bash
# Backend EC2 Setup Script for Stonk Market Analyzer

set -e

echo "=== Stonk Market Analyzer Backend Setup ==="

# Update system
echo "Updating system packages..."
sudo yum update -y || sudo apt-get update -y

# Install Python 3.9+
echo "Installing Python..."
sudo yum install python3 python3-pip -y || sudo apt-get install python3 python3-pip -y

# Install nginx for reverse proxy
echo "Installing nginx..."
sudo yum install nginx -y || sudo apt-get install nginx -y

# Create application directory
echo "Setting up application directory..."
sudo mkdir -p /opt/stonkmarketanalyzer
sudo chown -R $USER:$USER /opt/stonkmarketanalyzer
cd /opt/stonkmarketanalyzer

# Clone or copy application files (you'll need to upload these)
echo "Application files should be in /opt/stonkmarketanalyzer/backend"

# Install Python dependencies
echo "Installing Python dependencies..."
cd /opt/stonkmarketanalyzer/backend
pip3 install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/stonkmarketanalyzer.service > /dev/null <<EOF
[Unit]
Description=Stonk Market Analyzer Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/stonkmarketanalyzer/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/stonkmarketanalyzer/backend/.env
ExecStart=/usr/bin/python3 /opt/stonkmarketanalyzer/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
echo "Configuring nginx..."
sudo tee /etc/nginx/conf.d/stonkmarketanalyzer.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable stonkmarketanalyzer
sudo systemctl start stonkmarketanalyzer
sudo systemctl enable nginx
sudo systemctl restart nginx

echo "=== Backend setup complete! ==="
echo "Backend is running on port 3001"
echo "Nginx is proxying on port 80"
echo ""
echo "Check status with: sudo systemctl status stonkmarketanalyzer"
echo "View logs with: sudo journalctl -u stonkmarketanalyzer -f"
