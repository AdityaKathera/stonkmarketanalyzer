#!/bin/bash
# Setup self-signed SSL for backend (temporary solution)

EC2_IP="100.27.225.93"
SSH_KEY="/Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem"

echo "=== Setting up HTTPS for Backend ==="
echo ""

ssh -i "$SSH_KEY" ec2-user@$EC2_IP << 'ENDSSH'
    # Install certbot for Let's Encrypt (free SSL)
    echo "Installing certbot..."
    sudo yum install -y certbot python3-certbot-nginx || sudo dnf install -y certbot python3-certbot-nginx
    
    # Update nginx config for HTTPS
    echo "Updating nginx configuration..."
    sudo tee /etc/nginx/conf.d/stonkmarketanalyzer.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
EOF
    
    # Restart nginx
    sudo systemctl restart nginx
    
    echo ""
    echo "✓ Nginx configured with CORS support"
    echo ""
    echo "Backend is accessible at: http://$EC2_IP"
ENDSSH

echo ""
echo "=== Backend HTTPS Setup Complete ==="
echo ""
echo "Note: For production, you should:"
echo "1. Get a domain name"
echo "2. Use Let's Encrypt for free SSL certificate"
echo "3. Or use AWS Application Load Balancer with ACM certificate"
