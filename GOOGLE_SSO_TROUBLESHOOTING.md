# Google SSO Troubleshooting Guide

## Current Error: "Access blocked: Authorization Error"

### Root Causes
This error typically means Google is blocking the OAuth request due to configuration issues.

## Fix Steps

### 1. Google Cloud Console Configuration

#### A. OAuth Consent Screen
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Verify settings:
   - **App name**: Stonk Market Analyzer
   - **User support email**: Your email
   - **Authorized domains**: `stonkmarketanalyzer.com`
   - **Developer contact**: Your email
   - **Scopes**: email, profile, openid (default)

#### B. OAuth 2.0 Client ID
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on Client ID: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s`
3. Verify **Authorized JavaScript origins**:
   ```
   https://stonkmarketanalyzer.com
   https://www.stonkmarketanalyzer.com
   http://localhost:5173
   ```

4. Verify **Authorized redirect URIs**:
   ```
   https://stonkmarketanalyzer.com
   https://www.stonkmarketanalyzer.com
   http://localhost:5173
   https://stonkmarketanalyzer.com/
   https://www.stonkmarketanalyzer.com/
   http://localhost:5173/
   ```

### 2. Publishing Status

#### For Testing (Current)
- Keep OAuth consent screen in **"Testing"** mode
- Add your Google account to **"Test users"**:
  1. Go to OAuth consent screen
  2. Scroll to "Test users"
  3. Click "Add Users"
  4. Add your Gmail address

#### For Production (Later)
- Change to **"In production"** mode
- OR submit for Google verification (optional, takes 3-5 days)

### 3. Wait for Propagation
- Google changes take 5-10 minutes to propagate
- Clear browser cache or use incognito mode
- Try again

## Common Error Messages

### "Access blocked: This app's request is invalid"
- **Cause**: Authorized JavaScript origins missing
- **Fix**: Add your domain to authorized origins

### "Access blocked: Authorization Error"
- **Cause**: OAuth consent screen not configured or domain not authorized
- **Fix**: Complete OAuth consent screen setup and add authorized domain

### "Access blocked: This app is not verified"
- **Cause**: App in testing mode and user not in test users list
- **Fix**: Add your email to test users OR publish app

### "redirect_uri_mismatch"
- **Cause**: Redirect URI doesn't match configured URIs
- **Fix**: Add exact redirect URI to Google Console

## Debug Steps

### 1. Check Browser Console
Open browser DevTools (F12) and look for errors:
```javascript
// Look for messages like:
// "idpiframe_initialization_failed"
// "popup_closed_by_user"
// "access_denied"
```

### 2. Test with Different Browser
- Try Chrome incognito mode
- Try Firefox private window
- Clear all cookies and cache

### 3. Verify Environment Variables
Check that Client ID matches:

**Frontend** (`frontend/.env`):
```
VITE_GOOGLE_CLIENT_ID=735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com
```

**Backend** (`backend/.env`):
```
GOOGLE_CLIENT_ID=735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com
```

### 4. Test Locally First
```bash
cd frontend
npm run dev
```
- Go to http://localhost:5173
- Try Google Sign-In
- Check if it works locally before testing production

## Quick Checklist

- [ ] OAuth consent screen configured
- [ ] Authorized domains added (`stonkmarketanalyzer.com`)
- [ ] Authorized JavaScript origins added (all 3 URLs)
- [ ] Authorized redirect URIs added (all 6 URLs)
- [ ] Your email added to test users (if in testing mode)
- [ ] Waited 5-10 minutes after changes
- [ ] Cleared browser cache
- [ ] Client ID matches in both .env files

## Still Not Working?

### Option 1: Create New OAuth Client
Sometimes it's easier to start fresh:
1. Go to Google Cloud Console
2. Create new OAuth 2.0 Client ID
3. Configure all settings correctly
4. Update both .env files with new Client ID
5. Redeploy

### Option 2: Use Different Google Account
- Try signing in with a different Google account
- Make sure that account is in test users list

### Option 3: Check Google API Status
- Visit: https://status.cloud.google.com/
- Verify Google OAuth services are operational

## Contact Support

If nothing works:
1. Take screenshot of error
2. Take screenshot of Google Console OAuth settings
3. Check browser console for exact error message
4. Share these details for further debugging

---

**Most Common Fix**: Add your email to "Test users" in OAuth consent screen!
