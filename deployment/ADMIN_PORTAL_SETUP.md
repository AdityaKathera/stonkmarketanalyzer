# 🔒 Secure Admin Portal Setup Guide

## Security Features

✅ **Obscure URL Path** - Not /admin or any common path
✅ **JWT Authentication** - Token-based with 2-hour expiration
✅ **Password Hashing** - PBKDF2 with SHA-256 and salt
✅ **Unique Username** - Generated with random suffix
✅ **HTTPS Only** - Encrypted communication
✅ **No Common Names** - Custom generated credentials

## Step 1: Deploy Updated Backend

```bash
# Package backend with portal
tar -czf backend-portal.tar.gz -C backend .

# Upload to EC2
scp -i ~/Downloads/stonkmarketanalyzer-keypair.pem backend-portal.tar.gz ec2-user@100.27.225.93:/home/ec2-user/

# SSH and deploy
ssh -i ~/Downloads/stonkmarketanalyzer-keypair.pem ec2-user@100.27.225.93
```

On EC2:
```bash
# Stop service
sudo systemctl stop stonkmarketanalyzer

# Extract
sudo tar -xzf backend-portal.tar.gz -C /opt/stonkmarketanalyzer/backend

# Install new dependencies
cd /opt/stonkmarketanalyzer/backend
pip3 install pyjwt==2.8.0 psutil==5.9.6

# Generate secure credentials
python3 << 'EOF'
import secrets
portal_path = secrets.token_urlsafe(12).replace('-', '').replace('_', '')[:12]
portal_username = f"sentinel_{secrets.token_hex(4)}"
portal_salt = secrets.token_hex(32)
portal_secret = secrets.token_urlsafe(64)

print(f"\n🔐 SAVE THESE CREDENTIALS SECURELY:\n")
print(f"PORTAL_PATH={portal_path}")
print(f"PORTAL_USERNAME={portal_username}")
print(f"PORTAL_SALT={portal_salt}")
print(f"PORTAL_SECRET_KEY={portal_secret}")
print(f"\nPortal URL: https://api.stonkmarketanalyzer.com/api/{portal_path}/auth")
EOF

# Add to .env file (replace with actual values from above)
sudo tee -a /opt/stonkmarketanalyzer/backend/.env > /dev/null <<'EOF'

# Secure Admin Portal Configuration
PORTAL_PATH=your_generated_path_here
PORTAL_USERNAME=your_generated_username_here
PORTAL_SALT=your_generated_salt_here
PORTAL_SECRET_KEY=your_generated_secret_here
EOF

# Start service
sudo systemctl start stonkmarketanalyzer

# Check logs for portal info
sudo journalctl -u stonkmarketanalyzer -n 20
```

## Step 2: Set Your Password (First Time Only)

```bash
# From your local machine, set your password
curl -X POST https://api.stonkmarketanalyzer.com/api/YOUR_PORTAL_PATH/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_CHOSEN_PASSWORD"}'

# This will return a password hash
# Copy the hash and add it to .env on EC2
```

On EC2:
```bash
# Add password hash to .env
sudo nano /opt/stonkmarketanalyzer/backend/.env

# Add this line:
PORTAL_PASSWORD_HASH=the_hash_you_received

# Restart
sudo systemctl restart stonkmarketanalyzer
```

## Step 3: Deploy Admin Portal Frontend

```bash
# Create S3 bucket for admin portal
aws s3 mb s3://stonk-portal-$(date +%s) --region us-east-1

# Set bucket name
PORTAL_BUCKET="stonk-portal-XXXXX"  # Use actual bucket name

# Upload admin portal
aws s3 cp admin-portal/index.html s3://$PORTAL_BUCKET/index.html \
    --content-type "text/html" \
    --cache-control "no-cache"

# Configure for static website
aws s3 website s3://$PORTAL_BUCKET \
    --index-document index.html

# Make public (or use CloudFront for better security)
aws s3api put-bucket-policy \
    --bucket $PORTAL_BUCKET \
    --policy "{
        \"Version\": \"2012-10-17\",
        \"Statement\": [{
            \"Sid\": \"PublicReadGetObject\",
            \"Effect\": \"Allow\",
            \"Principal\": \"*\",
            \"Action\": \"s3:GetObject\",
            \"Resource\": \"arn:aws:s3:::$PORTAL_BUCKET/*\"
        }]
    }"

# Get portal URL
echo "Portal URL: http://$PORTAL_BUCKET.s3-website-us-east-1.amazonaws.com"
```

## Step 4: Update Portal HTML

Before uploading, update the `PORTAL_PATH` in `admin-portal/index.html`:

```javascript
const PORTAL_PATH = 'YOUR_GENERATED_PATH'; // Line 234
```

## Step 5: Access Your Portal

1. **Portal URL**: http://your-portal-bucket.s3-website-us-east-1.amazonaws.com
2. **Username**: (from Step 1 - starts with sentinel_)
3. **Password**: (what you set in Step 2)

## Security Best Practices

### ✅ DO:
- Keep credentials in a password manager
- Use a strong, unique password (20+ characters)
- Access only from trusted networks
- Enable 2FA on your AWS account
- Regularly rotate credentials
- Monitor access logs

### ❌ DON'T:
- Share credentials
- Use common passwords
- Access from public WiFi without VPN
- Store credentials in code
- Use the same password elsewhere

## Advanced: IP Whitelist (Optional)

Add IP restriction in nginx:

```bash
# On EC2
sudo nano /etc/nginx/conf.d/stonkmarketanalyzer.conf

# Add inside the server block:
location ~ ^/api/YOUR_PORTAL_PATH/ {
    allow YOUR_IP_ADDRESS;
    deny all;
    
    proxy_pass http://127.0.0.1:3001;
    # ... rest of proxy config
}

sudo systemctl restart nginx
```

## Monitoring

### Check Portal Access Logs

```bash
# On EC2
sudo journalctl -u stonkmarketanalyzer | grep "portal"
```

### View Analytics

The portal shows:
- Daily/Weekly user stats
- Most analyzed stocks
- System health (CPU, memory, disk)
- Event breakdown

## Troubleshooting

### Can't login?
1. Check credentials are correct
2. Verify password hash is set in .env
3. Check backend logs: `sudo journalctl -u stonkmarketanalyzer -f`
4. Verify HTTPS is working

### Portal not loading?
1. Check S3 bucket is public
2. Verify PORTAL_PATH in HTML matches backend
3. Check browser console for errors

### Token expired?
- Tokens expire after 2 hours
- Just login again
- Token is stored in browser localStorage

## Credentials Template

Save this securely (use a password manager):

```
Portal URL: http://[bucket-name].s3-website-us-east-1.amazonaws.com
API Endpoint: https://api.stonkmarketanalyzer.com/api/[portal-path]
Username: sentinel_[random]
Password: [your-strong-password]
Portal Path: [12-char-random]
```

## Future Enhancements

You can add to the portal:
- User management
- API key management
- Feature flags
- System configuration
- Database backups
- Email notifications
- Custom reports
- A/B testing controls

---

**🔒 Keep these credentials secure! This portal has full access to your analytics and system.**
