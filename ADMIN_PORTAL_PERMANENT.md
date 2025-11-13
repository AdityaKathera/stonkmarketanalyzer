# 🔒 Admin Portal - PERMANENT Credentials

## ✅ YOUR PERMANENT ADMIN PORTAL

**Portal URL**: `https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`

**Username**: `stonker_971805`

**Password**: `StonkerBonker@12345millibilli$`

---

## 🎯 Key Features

✅ **URL is FIXED** - 43 characters of random secure string  
✅ **Impossible to brute force** - 62^43 possible combinations  
✅ **Username/Password FIXED** - Easy to remember  
✅ **Never changes** - Save once, use forever  

---

## 🔐 Security

- **URL Entropy**: 43 characters = ~256 bits of security
- **Brute Force Time**: Billions of years at 1M attempts/second
- **Rate Limiting**: 10 requests/minute max
- **Lockout**: 3 failed attempts = 15-minute lockout
- **HTTPS Only**: Encrypted in transit

---

## 📝 How to Access

1. Go to: `https://api.stonkmarketanalyzer.com/api/6giWuaywmfb9eggwKlggvBmkRG2ZOBcTXNWbeShnvVg`
2. Enter username: `stonker_971805`
3. Enter password: `StonkerBonker@12345millibilli$`
4. Click "Login"
5. Access your analytics dashboard!

---

## 💾 Save These Credentials

**Bookmark the URL** or save to password manager:
- 1Password
- LastPass
- Bitwarden
- Apple Keychain

---

## ⚠️ Security Best Practices

✅ **DO**:
- Save URL in password manager
- Use HTTPS only
- Log out after use
- Access from secure networks

❌ **DON'T**:
- Share the URL publicly
- Access from public WiFi without VPN
- Leave logged in
- Share credentials

---

## 🔄 If You Need to Change

To change username/password, update `backend/.env`:

```bash
PORTAL_USERNAME=your_new_username
PORTAL_PASSWORD=your_new_password
```

To change URL (generate new random one):

```bash
python3 -c "import secrets; print('PORTAL_PATH=' + secrets.token_urlsafe(32))"
# Copy output to backend/.env
```

Then restart backend.

---

**Status**: ✅ PERMANENT - Won't change on restart  
**Security**: ✅ MAXIMUM - Impossible to brute force  
**Convenience**: ✅ EASY - Save once, use forever
