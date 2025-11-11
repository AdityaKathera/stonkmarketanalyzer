# Admin Portal Password Reset Instructions

## Your New Credentials

**Username:** `sentinel_65d3d147`  
**Password:** `7f16be4f677890d77e3b`  
**Portal URL:** http://stonk-portal-1762847505.s3-website-us-east-1.amazonaws.com

## How to Apply the Reset

### Option 1: Run the Reset Script (Recommended)

1. **Upload the script to your EC2 instance:**
   ```bash
   scp -i <your-key.pem> deployment/reset-admin-password.sh ec2-user@100.27.225.93:/home/ec2-user/
   ```

2. **SSH into your EC2 instance:**
   ```bash
   ssh -i <your-key.pem> ec2-user@100.27.225.93
   ```

3. **Run the reset script:**
   ```bash
   chmod +x reset-admin-password.sh
   ./reset-admin-password.sh
   ```

### Option 2: Manual Update

If you prefer to update manually:

1. **SSH into your EC2 instance:**
   ```bash
   ssh -i <your-key.pem> ec2-user@100.27.225.93
   ```

2. **Edit the .env file:**
   ```bash
   sudo nano /opt/stonkmarketanalyzer/backend/.env
   ```

3. **Add these lines (keep your existing PERPLEXITY_API_KEY):**
   ```
   ADMIN_USERNAME=sentinel_65d3d147
   ADMIN_PASSWORD_HASH=9e5af2ee9b82b8da88be76150666fc15:b574a54dda0c8efa8586f1f6cdb567343c18e9caf111a9a14b54f2b74794b9caeb82c8942aa726c4745e86c12b746a4ed5aa3020725c9c80ce23450ed6ff8d2f
   JWT_SECRET=stonk_jwt_secret_$(openssl rand -hex 32)
   PORTAL_PATH=iITXdYyGypK6
   ```

4. **Restart the backend service:**
   ```bash
   sudo systemctl restart stonkmarketanalyzer
   ```

5. **Verify it's running:**
   ```bash
   sudo systemctl status stonkmarketanalyzer
   ```

## After Reset

1. Go to: http://stonk-portal-1762847505.s3-website-us-east-1.amazonaws.com
2. Login with:
   - Username: `sentinel_65d3d147`
   - Password: `7f16be4f677890d77e3b`
3. Save these credentials in your password manager
4. Delete this file after saving credentials

## Troubleshooting

If the portal doesn't work after reset:

```bash
# Check backend logs
sudo journalctl -u stonkmarketanalyzer -n 50

# Test the API directly
curl http://localhost:3001/api/iITXdYyGypK6/health
```

## EC2 Instance Details

- **Public IP:** 100.27.225.93
- **Backend Path:** /opt/stonkmarketanalyzer/backend
- **Service Name:** stonkmarketanalyzer
