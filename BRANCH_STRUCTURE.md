# Branch Structure

This repository has two branches for different deployment targets:

## 🌐 `main` Branch (Production Web App)
**Status:** ✅ LIVE and WORKING  
**URL:** https://stonkmarketanalyzer.com  
**Purpose:** Production web application  

### What's in main:
- Working web frontend (React + Vite)
- Backend API (Python + Flask)
- Deployment scripts
- All documentation
- **NO mobile app code**

### Deploy web app:
```bash
git checkout main
cd frontend
npm run build
./deployment/deploy-frontend.sh
```

---

## 📱 `mobile-app` Branch (Mobile Development)
**Status:** 🚧 IN DEVELOPMENT  
**Purpose:** Android and iOS mobile apps  

### What's in mobile-app:
- Everything from `main` branch
- Capacitor mobile wrapper
- Android project (`frontend/android/`)
- iOS project (`frontend/ios/`)
- Mobile-specific CSS fixes
- Mobile deployment guides

### Test mobile app:
```bash
git checkout mobile-app
cd frontend
npm run build
npx cap sync android
npx cap open android
```

---

## How to Switch Between Branches

### Work on Web App (main):
```bash
git checkout main
# Make changes...
git add .
git commit -m "Your changes"
git push origin main
```

### Work on Mobile App:
```bash
git checkout mobile-app
# Make changes...
git add .
git commit -m "Your changes"
git push origin mobile-app
```

### Sync changes from main to mobile-app:
```bash
git checkout mobile-app
git merge main
# Resolve any conflicts
git push origin mobile-app
```

---

## Deployment Strategy

### Web App (Always Safe)
The `main` branch is your production web app. It's stable and working.
- Deploy anytime without risk
- No mobile dependencies
- Fast and reliable

### Mobile App (Test First)
The `mobile-app` branch has additional mobile code.
- Test thoroughly before releasing
- Build APK/AAB for Android
- Build IPA for iOS
- Submit to app stores

---

## Rollback Strategy

### If mobile app breaks:
```bash
# Just switch back to main branch
git checkout main

# Web app still works perfectly!
# Mobile changes are isolated in mobile-app branch
```

### If you need to revert mobile changes:
```bash
git checkout mobile-app
git log  # Find the last working commit
git reset --hard <commit-hash>
git push origin mobile-app --force
```

---

## Current Status

### ✅ Working (main branch):
- Web application
- Backend API
- All features functional
- Deployed and live

### 🚧 In Progress (mobile-app branch):
- Android app created
- iOS app created
- Fixing scrolling issues
- Testing in emulator
- Not yet released to stores

---

## Quick Commands

```bash
# Check current branch
git branch

# See all branches
git branch -a

# Switch to web version
git checkout main

# Switch to mobile version
git checkout mobile-app

# See what changed between branches
git diff main mobile-app

# Pull latest changes
git pull origin main
git pull origin mobile-app
```

---

## Safety Notes

1. **main branch = Production** - Don't break this!
2. **mobile-app branch = Experimental** - Safe to test here
3. **Always commit before switching branches**
4. **Test mobile changes before merging to main**
5. **Web app is independent of mobile app**

---

## When to Merge mobile-app into main?

Only merge when:
- [ ] Mobile app works perfectly
- [ ] All features tested
- [ ] No breaking changes to web app
- [ ] Ready to maintain both versions

Until then, keep them separate for safety!

---

**Current Recommendation:** Keep branches separate until mobile app is fully tested and released to app stores.
