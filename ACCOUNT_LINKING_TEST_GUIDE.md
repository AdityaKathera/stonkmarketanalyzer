# Account Linking - Testing Guide

## Quick Test Scenarios

### Scenario 1: Link Google to Existing Email Account

**Steps:**
1. Go to https://stonkmarketanalyzer.com
2. Login with email/password (existing account)
3. Click profile picture → Profile
4. Click "🔗 Linked Accounts" tab
5. Click "Link Google Account" button
6. Sign in with Google (use same email)
7. ✅ Should see success message
8. ✅ Should see both Email and Google in linked accounts
9. ✅ Email should be marked as "Primary"

**Expected Result:**
- Google account linked successfully
- Both providers shown in list
- Can now login with either method

### Scenario 2: Set Google as Primary Method

**Steps:**
1. After linking Google (from Scenario 1)
2. Find Google account card
3. Click "Set as Primary" button
4. ✅ Should see success message
5. ✅ Google should now have "Primary" badge
6. ✅ Email should no longer have "Primary" badge

**Expected Result:**
- Primary method changed to Google
- Badge moved to Google account

### Scenario 3: Try to Unlink Last Method (Should Fail)

**Steps:**
1. If you only have one method linked
2. Try to click "Unlink" button
3. ✅ Should see error: "Cannot unlink. Please set a password first."

**Expected Result:**
- Unlinking prevented
- Clear error message shown
- User must have at least one method

### Scenario 4: Unlink Google Account

**Steps:**
1. Make sure you have both Email and Google linked
2. Click "Unlink" button on Google account
3. Confirm in dialog
4. ✅ Should see success message
5. ✅ Google account removed from list
6. ✅ Only Email method remains
7. ✅ Email automatically set as Primary

**Expected Result:**
- Google account unlinked
- Can still login with email/password
- Primary method switched to email

### Scenario 5: New User Signs Up with Google

**Steps:**
1. Logout completely
2. Click "Sign Up" or "Login"
3. Click "Continue with Google"
4. Sign in with Google (new email not in system)
5. ✅ Account created automatically
6. ✅ Logged in successfully
7. Go to Profile → Linked Accounts
8. ✅ Should see Google as only method
9. ✅ Google marked as Primary

**Expected Result:**
- New account created with Google
- Google is primary method
- Can add email/password later

### Scenario 6: Existing User Signs In with Google (Auto-Link)

**Steps:**
1. Create account with email/password
2. Logout
3. Click "Login"
4. Click "Continue with Google"
5. Sign in with Google (same email as account)
6. ✅ Logged in successfully
7. Go to Profile → Linked Accounts
8. ✅ Should see both Email and Google linked
9. ✅ Google automatically linked

**Expected Result:**
- Google auto-linked to existing account
- Both methods available
- No duplicate account created

### Scenario 7: Try to Link Different Google Email (Should Fail)

**Steps:**
1. Login with email: user@example.com
2. Go to Profile → Linked Accounts
3. Click "Link Google Account"
4. Sign in with Google using different email: other@example.com
5. ✅ Should see error: "Google account email does not match"

**Expected Result:**
- Linking prevented
- Clear error message
- Email must match account email

## Visual Checks

### Linked Accounts Tab Should Show:
- ✅ Clean card-based layout
- ✅ Provider icons (🔵 for Google, 📧 for Email)
- ✅ "Primary" badge on primary method
- ✅ "Set as Primary" button on non-primary methods
- ✅ "Unlink" button on Google (if multiple methods)
- ✅ "Link Google Account" section (if Google not linked)
- ✅ Info messages at bottom

### Dark Mode Check:
1. Toggle dark mode
2. ✅ All cards should have dark background
3. ✅ Text should be readable
4. ✅ Buttons should have proper contrast
5. ✅ Hover effects should work

### Mobile Check:
1. Open on mobile or resize browser
2. ✅ Cards should stack vertically
3. ✅ Buttons should be full width
4. ✅ Text should be readable
5. ✅ No horizontal scrolling

## API Testing (Optional)

### Test with cURL:

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST https://api.stonkmarketanalyzer.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}' \
  | jq -r '.token')

# 2. Get linked accounts
curl -X GET https://api.stonkmarketanalyzer.com/api/auth/linked-accounts \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected output:
# {
#   "linked_accounts": [
#     {
#       "provider": "email",
#       "is_primary": true,
#       "linked_at": null
#     }
#   ]
# }
```

## Common Issues & Solutions

### Issue: "Google token is required"
**Solution:** Make sure Google OAuth is properly configured in frontend

### Issue: "Google account email does not match"
**Solution:** Use the same email for Google as your account email

### Issue: "Cannot unlink Google account"
**Solution:** You need at least one authentication method. Set a password first.

### Issue: "This Google account is already linked to another user"
**Solution:** This Google account is used by a different account. Use a different Google account.

### Issue: Changes not showing
**Solution:** Wait 2-3 minutes for CloudFront cache to clear, then hard refresh (Cmd+Shift+R)

## Success Criteria

- [x] Backend deployed and running
- [x] Frontend deployed to S3
- [x] CloudFront cache invalidated
- [ ] Can link Google to email account
- [ ] Can unlink Google account
- [ ] Can set primary method
- [ ] Auto-linking works on Google sign-in
- [ ] Validation prevents unlinking last method
- [ ] UI looks good in light mode
- [ ] UI looks good in dark mode
- [ ] Mobile responsive works
- [ ] Error messages are clear
- [ ] Success messages show

## Testing URLs

- **Production**: https://stonkmarketanalyzer.com
- **API Health**: https://api.stonkmarketanalyzer.com/api/health
- **Profile Page**: https://stonkmarketanalyzer.com (login → click profile → Profile)

## Notes

- Wait 2-3 minutes after deployment for CloudFront cache to clear
- Use hard refresh (Cmd+Shift+R or Ctrl+Shift+R) if changes don't appear
- Check browser console for any JavaScript errors
- Check backend logs if API calls fail

---

**Ready to test!** Start with Scenario 1 and work through each scenario.

