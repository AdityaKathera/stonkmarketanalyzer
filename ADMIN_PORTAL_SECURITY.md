# Admin Portal Security Implementation

## 🔒 Security Features Implemented

### 1. Rate Limiting
- **Max 10 requests per minute** per IP address
- Prevents automated scanning and brute force attacks
- Returns 429 error when limit exceeded

### 2. Account Lockout
- **3 failed login attempts** triggers 15-minute lockout
- Lockout applies per IP address
- Automatic unlock after lockout period
- Shows remaining attempts on failed login

### 3. Brute Force Protection
- 0.5 second delay on each login attempt (timing attack mitigation)
- Failed attempts tracked per IP
- Exponential backoff on repeated failures
- Logs all login attempts

### 4. IP Whitelist (Optional)
- Restrict access to specific IP addresses
- Set in backend `.env`: `PORTAL_ALLOWED_IPS=1.2.3.4,5.6.7.8`
- Disabled by default (empty = allow all)
- Returns 403 for non-whitelisted IPs

### 5. Obscure URL
- Admin portal NOT at `/admin.html`
- Random 24-character URL: `/DJIdaLCR7WkLDosAknR56uzd.html`
- Impossible to guess or brute force
- Not indexed by search engines

### 6. JWT Token Security
- Tokens expire after 2 hours
- Unique token ID (jti) prevents replay attacks
- Signed with secure secret key
- Automatic refresh on activity

### 7. Password Security
- PBKDF2 hashing with 100,000 iterations
- Unique salt per installation
- SHA-256 algorithm
- Password never stored in plaintext

### 8. Request Security
- HTTPS only (enforced)
- CORS protection
- X-Forwarded-For header support (proxy-aware)
- Real IP detection

---

## 📍 New Admin Portal URL

**KEEP THIS SECRET!**

```
https://stonkmarketanalyzer.com/DJIdaLCR7WkLDosAknR56uzd.html
```

**DO NOT SHARE THIS URL PUBLICLY!**

---

## 🔑 Login Credentials

**Username:** sentinel_65d3d147  
**Password:** [Your secure password]

**API Endpoint:** https://api.stonkmarketanalyzer.com/api/iITXdYyGypK6

---

## 🛡️ Security Best Practices

### For Maximum Security:

1. **Enable IP Whitelist**
   ```bash
   # On EC2, edit .env
   PORTAL_ALLOWED_IPS=your.home.ip,your.office.ip
   ```

2. **Use Strong Password**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Use a password manager

3. **Bookmark the URL**
   - Don't type it manually
   - Don't share via email/chat
   - Store in password manager

4. **Monitor Access**
   - Check backend logs regularly
   - Look for failed login attempts
   - Alert on suspicious activity

5. **Rotate Credentials**
   - Change password every 90 days
   - Regenerate portal path annually
   - Update JWT secret key periodically

---

## 🚨 What Happens on Attack

### Scenario 1: Brute Force Attack
```
Attempt 1: Wrong password → "Invalid credentials, 2 attempts left"
Attempt 2: Wrong password → "Invalid credentials, 1 attempt left"
Attempt 3: Wrong password → "Account locked for 15 minutes"
Next 15 min: All requests → 429 error
After 15 min: Lockout cleared, can try again
```

### Scenario 2: Rate Limit Exceeded
```
Request 1-10: Normal processing
Request 11+: "Too many requests. Please slow down." (429 error)
After 1 minute: Rate limit resets
```

### Scenario 3: Unauthorized IP (if whitelist enabled)
```
Request from non-whitelisted IP: "Access denied from your IP" (403 error)
No further processing, immediate rejection
```

---

## 📊 Security Monitoring

### Check Failed Login Attempts
```bash
ssh ec2-user@100.27.225.93
sudo journalctl -u stonkmarketanalyzer | grep "SECURITY"
```

### View Locked IPs
Backend logs show:
- IP address
- Timestamp
- Lock duration
- Attempts count

---

## 🔧 Configuration

### Backend Environment Variables

```bash
# Required
PORTAL_PATH=iITXdYyGypK6
PORTAL_USERNAME=sentinel_65d3d147
PORTAL_PASSWORD_HASH=<your_hash>
PORTAL_SALT=<your_salt>
PORTAL_SECRET_KEY=<your_secret>

# Optional Security
PORTAL_ALLOWED_IPS=1.2.3.4,5.6.7.8  # Leave empty to allow all
```

### Adjust Security Settings

Edit `backend/secure_portal.py`:

```python
MAX_ATTEMPTS = 3  # Failed attempts before lockout
LOCKOUT_DURATION = 900  # 15 minutes in seconds
RATE_LIMIT_WINDOW = 60  # 1 minute
MAX_REQUESTS_PER_MINUTE = 10  # Max requests per minute
```

---

## 🔄 Updating Security

### Change Admin Portal URL

1. Generate new random path:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32)[:24])"
   ```

2. Rename file in S3:
   ```bash
   aws s3 mv s3://stonkmarketanalyzer-frontend/DJIdaLCR7WkLDosAknR56uzd.html \
              s3://stonkmarketanalyzer-frontend/NEW_RANDOM_PATH.html
   ```

3. Update your bookmark

### Reset Password

```bash
ssh ec2-user@100.27.225.93
cd /opt/stonkmarketanalyzer
./deployment/reset-admin-password.sh
```

### Clear Lockouts (Emergency)

```bash
# Restart backend to clear in-memory lockouts
sudo systemctl restart stonkmarketanalyzer
```

---

## ⚠️ Security Warnings

### DO NOT:
- ❌ Share the admin portal URL
- ❌ Use weak passwords
- ❌ Access from public WiFi without VPN
- ❌ Leave browser logged in on shared computers
- ❌ Disable security features

### DO:
- ✅ Use HTTPS only
- ✅ Enable IP whitelist if possible
- ✅ Monitor access logs
- ✅ Use strong, unique password
- ✅ Log out after use
- ✅ Keep credentials in password manager

---

## 🆘 Emergency Procedures

### If Portal is Compromised:

1. **Immediately change password**
   ```bash
   ./deployment/reset-admin-password.sh
   ```

2. **Change portal path**
   - Generate new random URL
   - Move file in S3
   - Update backend PORTAL_PATH

3. **Enable IP whitelist**
   - Add only your IP
   - Restart backend

4. **Check logs for unauthorized access**
   ```bash
   sudo journalctl -u stonkmarketanalyzer | grep "SECURITY"
   ```

5. **Rotate JWT secret**
   - Generate new secret key
   - Update PORTAL_SECRET_KEY in .env
   - Restart backend

---

## 📈 Security Levels

### Level 1: Basic (Current)
- ✅ Obscure URL
- ✅ Rate limiting
- ✅ Account lockout
- ✅ Strong password hashing
- ✅ JWT tokens

### Level 2: Enhanced (Recommended)
- ✅ All Level 1 features
- ✅ IP whitelist enabled
- ✅ VPN required
- ✅ Regular password rotation

### Level 3: Maximum (Optional)
- ✅ All Level 2 features
- ✅ 2FA/TOTP authentication
- ✅ Hardware security key
- ✅ Audit logging to external service
- ✅ Intrusion detection system

---

## 🎯 Summary

Your admin portal now has:
- **Brute force protection** - 3 attempts, 15-min lockout
- **Rate limiting** - 10 requests/minute max
- **Obscure URL** - Impossible to guess
- **Strong encryption** - PBKDF2 + SHA-256
- **IP tracking** - Logs all access attempts
- **Optional whitelist** - Restrict to your IPs

**The portal is now highly secure against automated attacks and brute force attempts!**

---

**Last Updated:** November 12, 2025  
**Security Level:** High  
**Status:** ✅ Production Ready
