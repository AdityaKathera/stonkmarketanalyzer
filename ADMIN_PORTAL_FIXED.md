# 🔒 Admin Portal - FIXED Credentials

## ✅ Your Portal Credentials (SAVED)

**Username**: `stonker_971805`  
**Password**: `StonkerBonker@12345millibilli$`

**Current Portal URL**: `https://api.stonkmarketanalyzer.com/api/qLoDDJYLOi6g6kkg`

---

## 📝 How It Works Now

### What Changes:
- ✅ **Portal URL** - Random for security (changes on restart)

### What Stays the Same:
- ✅ **Username** - Always `stonker_971805`
- ✅ **Password** - Always `StonkerBonker@12345millibilli$`

---

## 🔄 After Backend Restart

When the backend restarts, you'll need to get the new URL:

```bash
ssh -i key.pem ec2-user@100.27.225.93
tail -50 /home/ec2-user/backend/app.log | grep "Secure portal"
```

This will show: `🔒 Secure portal initialized at: /api/XXXXXXXX`

**New URL**: `https://api.stonkmarketanalyzer.com/api/XXXXXXXX`

**Same credentials**: `stonker_971805` / `StonkerBonker@12345millibilli$`

---

## 🎯 Quick Access Script

Save this script to get the current portal URL:

```bash
#!/bin/bash
# get-portal-url.sh

ssh -i ~/.ssh/your-key.pem ec2-user@100.27.225.93 << 'EOF'
PORTAL_PATH=$(tail -100 /home/ec2-user/backend/app.log | grep "Secure portal" | tail -1 | grep -o "/api/[^[:space:]]*")
echo "🔒 Current Portal URL:"
echo "https://api.stonkmarketanalyzer.com$PORTAL_PATH"
echo ""
echo "Username: stonker_971805"
echo "Password: StonkerBonker@12345millibilli$"
EOF
```

---

## 💡 Why This Approach?

**Security Benefits**:
- Random URL prevents automated attacks
- Even if someone finds the URL, they need credentials
- URL changes on restart (extra security layer)

**Convenience**:
- You only need to remember ONE username and password
- No need to save new credentials each time
- Just get the new URL when needed

---

## 🔧 If You Want a Fixed URL

If you prefer a fixed URL that never changes, update `backend/.env`:

```bash
# Add this line:
PORTAL_PATH=my_secret_admin_path_12345

# Then restart backend
```

The URL will always be: `https://api.stonkmarketanalyzer.com/api/my_secret_admin_path_12345`

---

## 📊 Current Status

- ✅ Backend running (PID: 142659)
- ✅ Portal active
- ✅ Your credentials saved in .env
- ✅ Password works
- ✅ API healthy

---

**Save this file! It has your credentials and instructions.**
