# Google SSO Root Cause Fix - Access Blocked Error

## Current Status
- ✅ Publishing status: In production
- ❌ Users still getting "Access blocked: Authorization Error"

## Root Cause Analysis

The issue is that even though the app is published, Google requires **exact domain matching** between:
1. Where the request comes from (your website)
2. What's configured in Google Console

## The Fix - Step by Step

### Step 1: Verify OAuth Consent Screen Configuration

Go to: https://console.cloud.google.com/apis/credentials/consent

Click **"EDIT APP"** and verify each page:

#### Page 1: App Information
```
App name: Stonk Market Analyzer
User support email: [Your email]

Authorized domains:
✅ stonkmarketanalyzer.com

Developer contact information:
[Your email]
```

**CRITICAL**: The authorized domain must be EXACTLY `stonkmarketanalyzer.com` (no www, no https://)

Click **"SAVE AND CONTINUE"**

#### Page 2: Scopes
Verify you ONLY have these scopes (no sensitive scopes):
```
✅ .../auth/userinfo.email
✅ .../auth/userinfo.profile  
✅ openid
```

If you have any other scopes, REMOVE them (they require verification).

Click **"SAVE AND CONTINUE"**

#### Page 3: Test Users
You can leave this empty since you're in production.

Click **"SAVE AND CONTINUE"**

#### Page 4: Summary
Review and click **"BACK TO DASHBOARD"**

### Step 2: Fix OAuth Client Credentials

Go to: https://console.cloud.google.com/apis/credentials

Find your OAuth 2.0 Client ID: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s`

Click on it to edit.

#### Authorized JavaScript origins
**DELETE ALL** existing entries and add ONLY these (in this exact format):

```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

**DO NOT ADD**:
- ❌ http:// versions (only https://)
- ❌ Trailing slashes
- ❌ Paths like /callback

#### Authorized redirect URIs
**DELETE ALL** existing entries and add ONLY these:

```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

Click **"SAVE"**

### Step 3: Verify Domain Ownership (If Required)

If Google asks you to verify domain ownership:

1. Go to: https://console.cloud.google.com/apis/credentials/domainverification
2. Click **"+ ADD DOMAIN"**
3. Enter: `stonkmarketanalyzer.com`
4. Follow the verification steps (add TXT record to DNS)

### Step 4: Wait for Propagation

**IMPORTANT**: After making changes, you MUST wait:
- Minimum: 5 minutes
- Recommended: 10-15 minutes
- Maximum: 1 hour

Google needs time to propagate the changes across their servers.

### Step 5: Clear Browser Cache

Have users:
1. Clear browser cache completely
2. Or use incognito/private mode
3. Try signing in again

### Step 6: Test the Fix

1. Go to: https://stonkmarketanalyzer.com (or www version)
2. Click "Sign In"
3. Click "Sign in with Google"
4. Select Google account
5. Should work! ✅

## Common Mistakes That Cause This Error

### ❌ Mistake 1: Wrong Domain Format
```
Wrong: https://stonkmarketanalyzer.com
Right: stonkmarketanalyzer.com
```
In "Authorized domains" section, use domain only (no protocol).

### ❌ Mistake 2: Missing www Subdomain
If users access via www.stonkmarketanalyzer.com, you MUST have both:
- stonkmarketanalyzer.com (in authorized domains)
- https://www.stonkmarketanalyzer.com (in JavaScript origins)

### ❌ Mistake 3: Sensitive Scopes
If you have scopes beyond email/profile/openid, Google blocks unverified apps.

### ❌ Mistake 4: Not Waiting for Propagation
Changes take 5-15 minutes to propagate. Don't test immediately!

## Verification Checklist

Before testing, verify ALL of these:

**OAuth Consent Screen**:
- [ ] Publishing status: In production
- [ ] User type: External
- [ ] Authorized domains: `stonkmarketanalyzer.com` (no www, no https)
- [ ] Scopes: ONLY email, profile, openid
- [ ] No sensitive scopes

**OAuth Client Credentials**:
- [ ] Authorized JavaScript origins: `https://stonkmarketanalyzer.com` AND `https://www.stonkmarketanalyzer.com`
- [ ] Authorized redirect URIs: Same as above
- [ ] No http:// entries (only https://)
- [ ] No trailing slashes
- [ ] No localhost entries in production client

**Timing**:
- [ ] Waited at least 10 minutes after saving changes
- [ ] Cleared browser cache or using incognito

## If Still Not Working

### Debug Step 1: Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try signing in with Google
4. Look for error messages
5. Share the exact error message

### Debug Step 2: Check Network Tab
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try signing in with Google
4. Look for failed requests (red)
5. Click on the failed request
6. Check the Response tab
7. Share the error details

### Debug Step 3: Test with Different Domains
Try accessing from:
- https://stonkmarketanalyzer.com (no www)
- https://www.stonkmarketanalyzer.com (with www)

If one works and the other doesn't, you're missing that domain in the configuration.

## Alternative Solution: Create New OAuth Client

If nothing works, create a fresh OAuth client:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"OAuth client ID"**
4. Application type: **"Web application"**
5. Name: "Stonk Market Analyzer - Production"
6. Authorized JavaScript origins:
   ```
   https://stonkmarketanalyzer.com
   https://www.stonkmarketanalyzer.com
   ```
7. Authorized redirect URIs: (same as above)
8. Click **"CREATE"**
9. Copy the new Client ID
10. Update frontend/.env and backend/.env with new Client ID
11. Redeploy

## Expected Behavior After Fix

### For New Users (First Time)
1. Click "Sign in with Google"
2. Google popup opens
3. Select Google account
4. May see "This app isn't verified" warning
5. Click "Advanced" → "Go to Stonk Market Analyzer (unsafe)"
6. Grant permissions
7. Redirected back to app
8. Logged in! ✅

### For Returning Users
1. Click "Sign in with Google"
2. Google popup opens
3. Select Google account
4. Immediately logged in (no warnings) ✅

## To Remove "Unverified App" Warning

This is optional and takes 3-5 days:

1. Go to OAuth consent screen
2. Click "SUBMIT FOR VERIFICATION"
3. Fill out the verification form
4. Wait for Google review
5. Once approved, warning disappears

**Note**: The app works fine with the warning. Users just need to click "Advanced" once.

---

## Quick Command Reference

After fixing Google Console settings, update your app if needed:

```bash
# If you need to update Client ID in code:
# 1. Update frontend/.env
# 2. Update backend/.env
# 3. Rebuild and deploy

cd frontend
npm run build
aws s3 sync dist/ s3://stonkmarketanalyzer-frontend-1762843094/ --delete
aws cloudfront create-invalidation --distribution-id E2UZFZ0XAK8XWJ --paths "/*"

# Restart backend
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/.env ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

---

**Status**: Follow steps 1-6 above  
**Critical**: Wait 10-15 minutes after making changes  
**Test**: Use incognito mode to avoid cache issues
