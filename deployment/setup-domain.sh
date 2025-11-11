#!/bin/bash
# Quick domain setup script for stonkmarketanalyzer.com

DOMAIN="stonkmarketanalyzer.com"
API_SUBDOMAIN="api.$DOMAIN"

echo "Setting up domain: $DOMAIN"
echo "API subdomain: $API_SUBDOMAIN"

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo yum install -y certbot python3-certbot-nginx || sudo apt-get install -y certbot python3-certbot-nginx
fi

# Get SSL certificates
echo "Obtaining SSL certificates..."
sudo certbot --nginx -d $API_SUBDOMAIN --non-interactive --agree-tos --email your-email@example.com

# Update backend .env with proper CORS
echo "Updating backend configuration..."
sudo tee /opt/stonkmarketanalyzer/backend/.env > /dev/null <<EOF
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PORT=3001
NODE_ENV=production
ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://$API_SUBDOMAIN,http://localhost:5173
EOF

# Restart services
echo "Restarting services..."
sudo systemctl restart stonkmarketanalyzer
sudo systemctl reload nginx

echo "✅ Domain setup complete!"
echo "API endpoint: https://$API_SUBDOMAIN"
