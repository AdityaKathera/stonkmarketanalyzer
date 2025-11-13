# Google SSO Configuration Verification

## What You Need to Check Right Now

### 1. OAuth Consent Screen - Authorized Domains

Go to: https://console.cloud.google.com/apis/credentials/consent

Click **"EDIT APP"**

On the first page, look for **"Authorized domains"** section.

**What it should show**:
```
stonkmarketanalyzer.com
```

**Common mistakes**:
- ❌ `https://stonkmarketanalyzer.com` (has https://)
- ❌ `www.stonkmarketanalyzer.com` (has www)
- ❌ Empty (no domain added)

**If wrong**: 
1. Delete the wrong entry
2. Click "+ ADD DOMAIN"
3. Enter exactly: `stonkmarketanalyzer.com`
4. Click "SAVE AND CONTINUE" through all pages

---

### 2. OAuth Client - JavaScript Origins

Go to: https://console.cloud.google.com/apis/credentials

Click on: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s`

Look for **"Authorized JavaScript origins"** section.

**What it should show**:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

**Common mistakes**:
- ❌ Missing the www version
- ❌ Has http:// instead of https://
- ❌ Has trailing slashes
- ❌ Has localhost in production

**If wrong**:
1. Delete all existing entries
2. Click "+ ADD URI"
3. Add: `https://stonkmarketanalyzer.com`
4. Click "+ ADD URI" again
5. Add: `https://www.stonkmarketanalyzer.com`
6. Click "SAVE"

---

### 3. OAuth Client - Redirect URIs

In the same OAuth client settings.

Look for **"Authorized redirect URIs"** section.

**What it should show**:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
```

**If wrong**:
1. Delete all existing entries
2. Click "+ ADD URI"
3. Add: `https://stonkmarketanalyzer.com`
4. Click "+ ADD URI" again
5. Add: `https://www.stonkmarketanalyzer.com`
6. Click "SAVE"

---

### 4. Scopes Check

Go back to: https://console.cloud.google.com/apis/credentials/consent

Click **"EDIT APP"**

Go to the **"Scopes"** page (second page).

**What it should show**:
```
.../auth/userinfo.email
.../auth/userinfo.profile
openid
```

**If you see ANY other scopes**:
1. Click the X to remove them
2. Only keep the 3 basic scopes above
3. Click "SAVE AND CONTINUE"

---

## After Making Changes

### Step 1: Wait
- Set a timer for 10 minutes
- Do NOT test immediately
- Google needs time to propagate changes

### Step 2: Clear Cache
- Open incognito/private window
- Or clear browser cache completely

### Step 3: Test
1. Go to: https://stonkmarketanalyzer.com
2. Click "Sign In"
3. Click "Sign in with Google"
4. Should work!

---

## Quick Test Commands

Test if your domains are accessible:

```bash
# Test main domain
curl -I https://stonkmarketanalyzer.com

# Test www subdomain
curl -I https://www.stonkmarketanalyzer.com

# Both should return 200 OK
```

---

## Still Not Working?

If you've done all the above and waited 10+ minutes, the issue might be:

### Issue A: Domain Not Verified
- Go to: https://console.cloud.google.com/apis/credentials/domainverification
- Verify `stonkmarketanalyzer.com` is listed
- If not, add it and verify ownership

### Issue B: Wrong Project
- Make sure you're editing the correct Google Cloud project
- Check the project name at the top of the page

### Issue C: Multiple OAuth Clients
- You might have multiple OAuth clients
- Make sure you're using the correct Client ID in your code
- Check frontend/.env: `VITE_GOOGLE_CLIENT_ID`
- Check backend/.env: `GOOGLE_CLIENT_ID`
- Both should be: `735745800847-od596kg5vp2v7k66ghk7n1n5vndh8e0s.apps.googleusercontent.com`

---

## Emergency Fix: Add Users Manually

While troubleshooting, you can add users manually:

1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Scroll to **"Test users"**
3. Click **"+ ADD USERS"**
4. Add user emails (one per line)
5. Click "ADD"
6. Those users can sign in immediately

**Note**: This is temporary. Fix the root cause using steps above.

---

## Checklist

Before contacting support, verify:

- [ ] Authorized domains: `stonkmarketanalyzer.com` (no https, no www)
- [ ] JavaScript origins: Both https://stonkmarketanalyzer.com AND https://www.stonkmarketanalyzer.com
- [ ] Redirect URIs: Same as JavaScript origins
- [ ] Scopes: ONLY email, profile, openid
- [ ] Publishing status: In production
- [ ] Waited 10+ minutes after changes
- [ ] Tested in incognito mode
- [ ] Client ID matches in code

If all checked and still not working, share:
1. Screenshot of OAuth consent screen (authorized domains section)
2. Screenshot of OAuth client (JavaScript origins section)
3. Exact error message users see
4. Browser console error (F12 → Console tab)
