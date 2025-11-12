# 📦 Database Backup Guide

## Current Setup Summary

### What You Have:
- **Database**: SQLite (`users.db`)
- **Location**: `/home/ec2-user/backend/users.db` on EC2
- **Size**: 32 KB (4 users currently)
- **Tables**: users, portfolio, watchlist
- **Cost**: $0/month

### Security Status:
- ✅ bcrypt password hashing
- ✅ JWT tokens
- ✅ HTTPS enforced
- ⚠️ **No automated backups yet**

---

## 🎯 Recommendation: Keep SQLite + Add Backups

**Why SQLite is Perfect for You Right Now:**

1. **Cost**: $0 (vs $15-50/month for alternatives)
2. **Performance**: Fast enough for 10,000+ users
3. **Simplicity**: No external dependencies
4. **Reliability**: Proven technology
5. **Easy Migration**: Can move to RDS later if needed

**When to Migrate to RDS:**
- You have 5,000+ users
- You need high availability
- You're adding multiple servers
- Database > 1GB

**Estimated Timeline**: 6-12 months from now

---

## 🔒 Backup Strategy (3 Options)

### Option 1: Manual Backups (Immediate)

**Run this weekly:**
```bash
# Download database
scp -i ~/.ssh/key.pem ec2-user@100.27.225.93:/home/ec2-user/backend/users.db ./users-backup-$(date +%Y%m%d).db

# Keep on your local machine or upload to cloud storage
```

**Pros**: Simple, free, works immediately
**Cons**: Manual effort required
**Cost**: $0
**Time**: 2 minutes/week

---

### Option 2: Automated Local Backups (Recommended)

**Set up on your local machine (Mac/Linux):**

```bash
# Create backup script
cat > ~/backup-stonk-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
    ec2-user@100.27.225.93:/home/ec2-user/backend/users.db \
    ~/stonk-backups/users-$DATE.db

# Keep only last 30 backups
cd ~/stonk-backups
ls -t users-*.db | tail -n +31 | xargs rm -f
echo "Backup completed: users-$DATE.db"
EOF

# Make executable
chmod +x ~/backup-stonk-db.sh

# Create backup directory
mkdir -p ~/stonk-backups

# Test it
~/backup-stonk-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-stonk-db.sh >> ~/stonk-backups/backup.log 2>&1") | crontab -
```

**Pros**: Automated, free, reliable
**Cons**: Requires your computer to be on
**Cost**: $0
**Setup Time**: 5 minutes

---

### Option 3: S3 Backups (Best for Production)

**Set up automated S3 backups:**

```bash
# Use the provided script
./deployment/setup-db-backups.sh

# Or manually:
DATE=$(date +%Y%m%d-%H%M%S)
scp -i key.pem ec2-user@100.27.225.93:/home/ec2-user/backend/users.db /tmp/users-$DATE.db
aws s3 cp /tmp/users-$DATE.db s3://stonkmarketanalyzer-frontend-1762843094/backups/
rm /tmp/users-$DATE.db
```

**Pros**: Cloud storage, accessible anywhere, durable
**Cons**: Requires AWS credentials
**Cost**: ~$0.01/month (S3 storage)
**Setup Time**: 10 minutes

---

## 🚨 Disaster Recovery Plan

### If EC2 Instance Fails:

**1. Launch New EC2 Instance**
```bash
# Use existing launch template or create new one
```

**2. Restore Database**
```bash
# From local backup:
scp users-backup-YYYYMMDD.db ec2-user@NEW-IP:/home/ec2-user/backend/users.db

# From S3:
aws s3 cp s3://bucket/backups/users-backup-YYYYMMDD.db /tmp/users.db
scp /tmp/users.db ec2-user@NEW-IP:/home/ec2-user/backend/users.db
```

**3. Deploy Backend**
```bash
# Use existing deployment script
./deployment/deploy-auth-backend.sh
```

**Recovery Time**: 15-30 minutes

---

## 📊 Cost Comparison

| Solution | Setup Time | Monthly Cost | Reliability | Effort |
|----------|------------|--------------|-------------|--------|
| **Manual Backups** | 2 min | $0 | Medium | Weekly |
| **Local Automated** | 5 min | $0 | High | None |
| **S3 Automated** | 10 min | $0.01 | Very High | None |
| **RDS** | 2 hours | $15-30 | Highest | None |

---

## 🎯 My Recommendation

### For Now (Next 6 months):
**Option 2: Automated Local Backups** ✅

**Why**:
- Free
- Automated
- Reliable
- Easy to set up
- Perfect for your stage

**Action**: Run the setup script above (5 minutes)

### For Later (6-12 months):
**Migrate to RDS** when you hit 5,000 users

**Why**:
- Better reliability
- Automatic backups
- Can scale
- Worth the $20/month at that stage

---

## 🔧 Quick Setup (Do This Now)

**1. Create backup directory:**
```bash
mkdir -p ~/stonk-backups
```

**2. Create backup script:**
```bash
cat > ~/backup-stonk-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
    ec2-user@100.27.225.93:/home/ec2-user/backend/users.db \
    ~/stonk-backups/users-$DATE.db
ls -t ~/stonk-backups/users-*.db | tail -n +31 | xargs rm -f
echo "✅ Backup completed: users-$DATE.db"
EOF

chmod +x ~/backup-stonk-db.sh
```

**3. Test it:**
```bash
~/backup-stonk-db.sh
```

**4. Schedule it (optional):**
```bash
(crontab -l 2>/dev/null; echo "0 2 * * * ~/backup-stonk-db.sh >> ~/stonk-backups/backup.log 2>&1") | crontab -
```

**Done!** ✅ You now have automated daily backups.

---

## 📈 Monitoring

### Check Database Size:
```bash
ssh -i key.pem ec2-user@100.27.225.93 'ls -lh /home/ec2-user/backend/users.db'
```

### Check Number of Users:
```bash
ssh -i key.pem ec2-user@100.27.225.93 'sqlite3 /home/ec2-user/backend/users.db "SELECT COUNT(*) FROM users;"'
```

### Check Backup Status:
```bash
ls -lh ~/stonk-backups/
```

---

## 🎉 Summary

**Current Setup**: ✅ Perfect for MVP
- SQLite database
- 32 KB (4 users)
- $0/month
- Handles 10,000+ users

**Immediate Action**: Set up automated backups (5 minutes)

**Future Plan**: Migrate to RDS at 5,000 users ($20/month)

**You're using the cheapest, most efficient solution for your stage. Just add backups and you're golden!** 🚀

---

## 📚 Additional Resources

- `USER_MANAGEMENT_ANALYSIS.md` - Detailed comparison of all options
- `deployment/setup-db-backups.sh` - Automated backup script
- `AUTH_SETUP_GUIDE.md` - Authentication setup guide

**Questions?** Check the analysis document for detailed comparisons!
