# Production Setup Guide - Stonk Market Analyzer

This guide documents the exact production setup for quick recovery or redeployment.

## Current Production Environment

- **Domain**: stonkmarketanalyzer.com
- **API Domain**: api.stonkmarketanalyzer.com
- **EC2 Instance**: 100.27.225.93
- **SSH User**: ec2-user
- **Backend Port**: 3001
- **Frontend**: Served via nginx on port 80/443

## Prerequisites

1. AWS EC2 instance (Amazon Linux 2 or similar)
2. Domain configured with DNS pointing to EC2 IP
3. SSH key pair for EC2 access
4. Perplexity API key

## Quick Deployment from GitHub

### 1. Clone Repository

```bash
git clone https://github.com/AdityaKathera/stonkmarketanalyzer.git
cd stonkmarketanalyzer
```

### 2. Backend Setup on EC2

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@100.27.225.93

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip nginx -y

# Create application directory
sudo mkdir -p /opt/stonkmarketanalyzer
sudo chown -R ec2-user:ec2-user /opt/stonkmarketanalyzer

# Clone repo on server
cd /opt/stonkmarketanalyzer
git clone https://github.com/AdityaKathera/stonkmarketanalyzer.git .

# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Create .env file
cat > .env << EOF
PERPLEXITY_API_KEY=your_api_key_here
PORT=3001
NODE_ENV=production
ALLOWED_ORIGINS=https://stonkmarketanalyzer.com,https://www.stonkmarketanalyzer.com,https://api.stonkmarketanalyzer.com,http://localhost:5173
EOF

# Create systemd service
sudo tee /etc/systemd/system/stonkmarketanalyzer.service > /dev/null <<EOF
[Unit]
Description=Stonk Market Analyzer Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/stonkmarketanalyzer/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/stonkmarketanalyzer/backend/.env
ExecStart=/usr/bin/python3 /opt/stonkmarketanalyzer/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start backend
sudo systemctl daemon-reload
sudo systemctl enable stonkmarketanalyzer
sudo systemctl start stonkmarketanalyzer
```

### 3. Nginx Configuration

```bash
# Copy nginx config
sudo cp /opt/stonkmarketanalyzer/deployment/stonkmarketanalyzer.conf /etc/nginx/conf.d/

# Get SSL certificates
sudo yum install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.stonkmarketanalyzer.com --non-interactive --agree-tos --email your-email@example.com

# Restart nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### 4. Frontend Deployment

On your local machine:

```bash
cd stonkmarketanalyzer/frontend

# Create .env file
echo "VITE_API_URL=https://api.stonkmarketanalyzer.com" > .env

# Install dependencies and build
npm install
npm run build

# Deploy to EC2
scp -i your-key.pem -r dist/* ec2-user@100.27.225.93:/tmp/frontend/
ssh -i your-key.pem ec2-user@100.27.225.93 "sudo rm -rf /usr/share/nginx/html/* && sudo cp -r /tmp/frontend/* /usr/share/nginx/html/ && sudo chown -R nginx:nginx /usr/share/nginx/html/"
```

## Verification

1. **Backend Health**: `curl https://api.stonkmarketanalyzer.com/api/health`
2. **Frontend**: Visit https://stonkmarketanalyzer.com
3. **Backend Logs**: `sudo journalctl -u stonkmarketanalyzer -f`
4. **Nginx Logs**: `sudo tail -f /var/log/nginx/error.log`

## Important Files

### Backend
- `/opt/stonkmarketanalyzer/backend/app.py` - Main Flask app
- `/opt/stonkmarketanalyzer/backend/.env` - Environment variables (contains API key)
- `/etc/systemd/system/stonkmarketanalyzer.service` - Systemd service

### Nginx
- `/etc/nginx/conf.d/stonkmarketanalyzer.conf` - Nginx config
- `/etc/letsencrypt/live/api.stonkmarketanalyzer.com/` - SSL certificates

### Frontend
- `/usr/share/nginx/html/` - Built frontend files

## Troubleshooting

### Backend not starting
```bash
sudo systemctl status stonkmarketanalyzer
sudo journalctl -u stonkmarketanalyzer -n 50
```

### CORS errors
Check `ALLOWED_ORIGINS` in `/opt/stonkmarketanalyzer/backend/.env`

### SSL certificate issues
```bash
sudo certbot renew --dry-run
sudo certbot certificates
```

### Frontend not loading
```bash
ls -la /usr/share/nginx/html/
sudo nginx -t
sudo systemctl status nginx
```

## Updating Production

### Backend Update
```bash
ssh -i your-key.pem ec2-user@100.27.225.93
cd /opt/stonkmarketanalyzer
git pull origin main
sudo systemctl restart stonkmarketanalyzer
```

### Frontend Update
```bash
# Local machine
cd stonkmarketanalyzer/frontend
npm run build
./deployment/deploy-frontend.sh
```

## Rollback Procedure

If something breaks:

```bash
# On EC2
cd /opt/stonkmarketanalyzer
git log --oneline  # Find last working commit
git checkout <commit-hash>
sudo systemctl restart stonkmarketanalyzer
```

## Admin Portal

- **URL**: https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6
- **Username**: sentinel_65d3d147
- **Password**: Stored in `/opt/stonkmarketanalyzer/backend/.env` as PORTAL_PASSWORD_HASH

## Security Notes

1. Never commit `.env` files with real API keys
2. Keep SSH keys secure
3. Regularly update SSL certificates (auto-renewed by certbot)
4. Monitor backend logs for errors
5. Keep dependencies updated

## Contact

For issues, check:
- GitHub: https://github.com/AdityaKathera/stonkmarketanalyzer
- Live site: https://stonkmarketanalyzer.com
