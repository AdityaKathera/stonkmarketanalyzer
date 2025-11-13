# Google SSO Final Fix - Access Blocked Error

## Current Status
- ✅ Code deployed with useOneTap removed
- ✅ Publishing status: In production
- ❌ Still getting "Access blocked: Authorization Error"

## This Means: Google Console Configuration Issue

The error is NOT in the code - it's in your Google Cloud Console settings.

## Critical Checklist - Do These EXACTLY

### 1. OAuth Consent Screen - App Information

Go to: https://console.cloud.google.com/apis/credentials/consent

Click **"EDIT APP"**

#### Page 1: App Information

**Authorized domains** section:
```
✅ Must have: stonkmarketanalyzer.com
❌ NOT: https://stonkmarketanalyzer.com
❌ NOT: www.stonkmarketanalyzer.com
❌ NOT: Empty
```

**CRITICAL**: The domain must be EXACTLY `stonkmarketanalyzer.com` with:
- No `https://`
- No `www.`
- No trailing slash
- No path

If it's wrong:
1. Delete the wrong entry
2. Click "+ ADD DOMAIN"
3. Type EXACTLY: `stonkmarketanalyzer.com`
4. Press Enter
5. Click "SAVE AND CONTINUE"

#### Page 2: Scopes

**Must have ONLY these 3 scopes**:
```
✅ .../auth/userinfo.email
✅ .../auth/userinfo.profile
✅ openid
```

**If you have ANY other scopes, REMOVE them!**

Sensitive scopes require verification and will block unverified apps.

Click "SAVE AND CONTINUE"

#### Page 3: Test Users

**If Publishing Status is "Testing"**:
- Add your email and all user emails here
- Click "+ ADD USERS"
- Add one email per line
- Click "ADD"

**If Publishing Status is "In production"**:
- You can leave this empty
- All users should be able to sign in

Click "SAVE AND CONTINUE"

#### Page 4: Summary

Review everything and click "BACK TO DASHBOARD"

### 2. Verify Publishing Status

On the OAuth consent screen dashboard:

**Look for "Publishing status" at the top**:
- ✅ Should say: "In production" with green checkmark
- ❌ If it says "Testing": Click "PUBLISH APP" button

### 3. OAuth Client Credentials

Go to: https://console.cloud.google.com/apis/credentials

Find: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s`

Click on it.

#### Authorized JavaScript origins

**Must have EXACTLY these (nothing else)**:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

**Delete if you have**:
- ❌ `http://` versions (only https)
- ❌ Localhost entries (for production client)
- ❌ Trailing slashes
- ❌ Any paths like `/callback`

#### Authorized redirect URIs

**Must have EXACTLY these (nothing else)**:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

Same rules as JavaScript origins.

Click "SAVE"

### 4. Wait for Propagation

**CRITICAL**: After making ANY changes:
- Wait 10-15 minutes
- Do NOT test immediately
- Google needs time to propagate changes

Set a timer and wait!

### 5. Test Again

After waiting 15 minutes:
1. Open NEW incognito window
2. Go to: https://stonkmarketanalyzer.com
3. Click "Sign In"
4. Click "Sign in with Google"
5. Try signing in

## Common Mistakes That Cause This Error

### Mistake #1: Wrong Domain Format
```
❌ Wrong: https://stonkmarketanalyzer.com (in authorized domains)
✅ Right: stonkmarketanalyzer.com (no protocol)
```

### Mistake #2: Missing www Subdomain
If users access via www.stonkmarketanalyzer.com, you MUST have:
- In authorized domains: `stonkmarketanalyzer.com` (covers all subdomains)
- In JavaScript origins: BOTH `https://stonkmarketanalyzer.com` AND `https://www.stonkmarketanalyzer.com`

### Mistake #3: Extra Scopes
If you have scopes beyond email/profile/openid, Google blocks the app.

### Mistake #4: Testing Too Soon
Changes take 10-15 minutes to propagate. Testing immediately shows old error.

### Mistake #5: App Still in Testing Mode
Even if you think it's published, double-check the status shows "In production"

## Debug: Get Exact Error

Open browser console (F12) and look for errors. Share the EXACT error message.

Common error messages and their fixes:

### "redirect_uri_mismatch"
**Fix**: Add the exact redirect URI to OAuth client

### "invalid_client"
**Fix**: Client ID doesn't match or is wrong

### "access_denied"
**Fix**: User not in test users list (if in testing mode)

### "org_internal"
**Fix**: App is set to "Internal" but user is external

## Nuclear Option: Create New OAuth Client

If nothing works, create a fresh OAuth client:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "+ CREATE CREDENTIALS"
3. Select "OAuth client ID"
4. Application type: "Web application"
5. Name: "Stonk Market Analyzer - Production v2"
6. Authorized JavaScript origins:
   ```
   https://stonkmarketanalyzer.com
   https://www.stonkmarketanalyzer.com
   ```
7. Authorized redirect URIs: (same as above)
8. Click "CREATE"
9. Copy the new Client ID
10. Update `frontend/.env`:
    ```
    VITE_GOOGLE_CLIENT_ID=NEW_CLIENT_ID_HERE
    ```
11. Update `backend/.env`:
    ```
    GOOGLE_CLIENT_ID=NEW_CLIENT_ID_HERE
    ```
12. Rebuild and redeploy

## What to Share for Further Help

If still not working after all above steps, share:

1. **Screenshot of OAuth consent screen** (authorized domains section)
2. **Screenshot of OAuth client** (JavaScript origins section)
3. **Publishing status** (Testing or In production?)
4. **Exact error from browser console** (F12 → Console tab)
5. **Which URL are you accessing?** (with or without www?)

---

**Most likely issue**: Authorized domains not configured correctly or app still in testing mode without test users added.
