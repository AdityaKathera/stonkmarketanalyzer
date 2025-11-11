# 🔒 Secure Admin Portal

## Quick Deploy (Automated)

```bash
chmod +x deployment/deploy-admin-portal.sh
./deployment/deploy-admin-portal.sh
```

This script will:
1. ✅ Generate unique, secure credentials
2. ✅ Deploy backend with portal
3. ✅ Set up your password
4. ✅ Deploy portal frontend to S3
5. ✅ Give you access credentials

**Time: ~5 minutes**

## What You Get

### 📊 Analytics Dashboard
- Real-time user statistics
- Daily/Weekly trends
- Most analyzed stocks
- System health monitoring

### 🔐 Security Features
- **Obscure URL** - Not /admin or any common path
- **JWT Tokens** - 2-hour expiration
- **Password Hashing** - PBKDF2 + SHA-256
- **Unique Username** - Generated with random suffix
- **HTTPS Only** - Encrypted communication

### 🎯 Portal Features
- User analytics overview
- Popular stocks tracking
- 7-day trend analysis
- System health (CPU, memory, disk)
- Auto-refresh every 30 seconds
- Secure logout

## Manual Setup

If you prefer manual setup, follow: `deployment/ADMIN_PORTAL_SETUP.md`

## Access

After deployment, you'll receive:
- **Portal URL**: http://stonk-portal-XXXXX.s3-website-us-east-1.amazonaws.com
- **Username**: sentinel_XXXX (unique)
- **Password**: (what you set during deployment)

## Security Best Practices

✅ **DO:**
- Use a password manager
- Use 20+ character password
- Access from trusted networks only
- Rotate credentials regularly

❌ **DON'T:**
- Share credentials
- Use common passwords
- Access from public WiFi
- Store credentials in code

## Future Enhancements

The portal is designed to be extensible. You can add:
- User management
- API key management
- Feature flags
- Email notifications
- Custom reports
- A/B testing
- Database backups

## Support

For issues:
1. Check `deployment/ADMIN_PORTAL_SETUP.md`
2. View backend logs: `sudo journalctl -u stonkmarketanalyzer -f`
3. Check browser console for errors

---

**🔒 This portal has full access to your system. Keep credentials secure!**
