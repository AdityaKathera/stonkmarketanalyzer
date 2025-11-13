# ✅ COMPLETED: Account Linking

## Status: COMPLETE (November 13, 2024)

**Feature:** Account Linking - See `ACCOUNT_LINKING_COMPLETE.md` for details

---

# Next Session Task: TBD

## Task for Next AI Assistant

**User wants to build:** (To be determined)

## What is Account Linking?

Allow users to:
- Link their Google account to an existing email/password account
- Link multiple OAuth providers to one account
- Unlink providers
- Choose primary login method

## Why This Feature?

**User Story:**
- User signs up with email/password
- Later wants to use Google Sign-In
- Should be able to link Google to existing account
- All data stays with one account

## Current State

### What's Already Working
- ✅ Email/password authentication
- ✅ Google SSO (separate accounts)
- ✅ Profile page with account management
- ✅ User database with basic fields

### What Needs to Be Built

#### 1. Database Changes
Add to users table:
- `google_id` field (nullable)
- `auth_provider` field (email, google, or both)
- `primary_auth_method` field

#### 2. Backend Endpoints
- `POST /api/auth/link-google` - Link Google to current account
- `DELETE /api/auth/unlink-google` - Unlink Google
- `GET /api/auth/linked-accounts` - Get linked providers
- Update Google OAuth to check for existing email

#### 3. Frontend UI
Add to Profile page (new tab: "Linked Accounts"):
- Show linked providers
- "Link Google Account" button
- "Unlink" buttons for each provider
- Primary login method selector

#### 4. Logic to Handle
- User with email/password wants to link Google
- User with Google wants to link email/password
- Prevent duplicate Google accounts
- Handle unlinking (must keep at least one method)

## Implementation Plan

### Phase 1: Database (30 min)
1. Add migration to add new fields to users table
2. Update auth_service.py to handle new fields

### Phase 2: Backend (1 hour)
1. Create link-google endpoint
2. Update Google OAuth to check for existing accounts
3. Create unlink endpoint
4. Add validation (can't unlink last method)

### Phase 3: Frontend (1 hour)
1. Add "Linked Accounts" tab to Profile
2. Show current linked providers
3. Add "Link Google Account" button
4. Add unlink functionality
5. Style the UI

### Phase 4: Testing & Deployment (30 min)
1. Test linking flow
2. Test unlinking flow
3. Deploy backend and frontend
4. Verify in production

## Files to Modify

**Backend:**
- `backend/auth_service.py` - Add database fields
- `backend/auth_routes.py` - Add new endpoints
- `backend/users.db` - Schema update

**Frontend:**
- `frontend/src/components/Profile.jsx` - Add new tab
- `frontend/src/components/Profile.css` - Style linked accounts

## Expected Time

**Total: 2-3 hours**

## Success Criteria

- [ ] User can link Google to email/password account
- [ ] User can unlink providers (keeping at least one)
- [ ] No duplicate accounts created
- [ ] UI shows linked providers clearly
- [ ] Works in both light and dark modes
- [ ] Deployed to production

## Notes

- User is at: https://stonkmarketanalyzer.com
- Use `deploy-with-role.sh` for deployment
- All context in `AI_SESSION_CONTEXT.md`
- Phase 1 features are complete and working

---

**Ready to build!** Start by reading `START_HERE.md` and `AI_SESSION_CONTEXT.md` for full context.
