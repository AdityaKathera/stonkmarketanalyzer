# Test Google SSO Configuration

## Quick Diagnostic Test

Open your browser console on https://stonkmarketanalyzer.com and run this:

```javascript
// Check if Client ID is loaded
console.log('Client ID:', import.meta.env.VITE_GOOGLE_CLIENT_ID);

// Should show: 735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com
```

If it shows `undefined`, the environment variable isn't being loaded.

## Most Likely Issue: Client ID Not Loading

The error "Access blocked: Authorization Error" when everything is configured correctly in Google Console usually means the Client ID isn't being passed correctly to the Google OAuth library.

### Fix: Hardcode Client ID Temporarily

This will help us determine if it's an environment variable issue:

1. Open `frontend/src/components/AuthModal.jsx`
2. Find this line:
   ```javascript
   <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
   ```
3. Temporarily change it to:
   ```javascript
   <GoogleOAuthProvider clientId="735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com">
   ```
4. Rebuild and test

If this works, the issue is with environment variables not being loaded.

## Check Environment Variable

Run this locally:

```bash
cd frontend
cat .env
```

Should show:
```
VITE_API_URL=https://api.stonkmarketanalyzer.com
VITE_GOOGLE_CLIENT_ID=735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com
```

## Common Issues

### Issue 1: .env File Not in Build
Vite only includes environment variables that start with `VITE_` and only at build time.

**Solution**: Make sure you rebuild after changing .env:
```bash
cd frontend
npm run build
```

### Issue 2: Wrong Origin
The error might be because the request is coming from a different origin than configured.

**Check**: Are you accessing via:
- https://stonkmarketanalyzer.com (no www)
- https://www.stonkmarketanalyzer.com (with www)

Both need to be in Google Console.

### Issue 3: useOneTap Causing Issues
The `useOneTap` prop might be causing problems.

**Solution**: Remove it temporarily:
```javascript
<GoogleLogin
  onSuccess={handleGoogleSuccess}
  onError={handleGoogleError}
  // useOneTap  <- Remove this line
  theme="outline"
  size="large"
  text={mode === 'login' ? 'signin_with' : 'signup_with'}
/>
```

## Debug Steps

1. **Check if Client ID is defined**:
   - Open browser console
   - Type: `import.meta.env.VITE_GOOGLE_CLIENT_ID`
   - Should show the Client ID

2. **Check Network Requests**:
   - Open DevTools → Network tab
   - Click "Sign in with Google"
   - Look for requests to `accounts.google.com`
   - Check if Client ID is in the request

3. **Check Console Errors**:
   - Look for errors like:
     - "Invalid client ID"
     - "Origin mismatch"
     - "Unauthorized"

## The Real Fix

Based on the error, here's what's likely happening:

**The Client ID environment variable isn't being loaded in the production build.**

### Solution:

1. Verify `.env` file exists in `frontend/` directory
2. Rebuild with environment variables:
   ```bash
   cd frontend
   npm run build
   ```
3. Verify the build includes the Client ID:
   ```bash
   grep -r "735745800847" dist/
   ```
4. If not found, the env var isn't being included
5. Redeploy:
   ```bash
   aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete
   aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"
   ```

---

**Next Step**: Try the hardcoded Client ID fix above to confirm this is the issue.
