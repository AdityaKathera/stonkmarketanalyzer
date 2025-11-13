# Next Session Task: AI News Summarizer

## Task for Next AI Assistant

**User wants to build:** AI News Summarizer (Phase 2 - AI Features)

## What is AI News Summarizer?

Personalized news feed for user's watchlist stocks with AI-powered summaries and sentiment analysis.

## Features to Build

### 1. News Fetching Service
- Fetch latest news for watchlist stocks
- Use news API (NewsAPI, Alpha Vantage, or similar)
- Cache news for performance

### 2. AI Summarization
- Use Perplexity API to summarize news articles
- Sentiment analysis (bullish/bearish/neutral)
- Impact score on stock price
- Key takeaways in bullet points

### 3. Frontend UI
- New "News" tab or section
- News cards with summaries
- Sentiment indicators (color-coded)
- Filter by stock ticker
- Refresh functionality

## Implementation Plan

### Phase 1: Backend (1.5 hours)
1. Create `news_service.py` - Fetch news from API
2. Create `news_summarizer_service.py` - AI summarization
3. Add endpoint: `GET /api/news/watchlist`
4. Add endpoint: `GET /api/news/stock/{ticker}`
5. Implement caching (1 hour per stock)

### Phase 2: Frontend (1.5 hours)
1. Create `NewsSection.jsx` component
2. News card component with summary
3. Sentiment badges and icons
4. Filter and sort functionality
5. Loading states and error handling

### Phase 3: Integration (30 min)
1. Add to main app navigation
2. Test with real data
3. Polish UI/UX
4. Mobile responsive

### Phase 4: Deploy (30 min)
1. Deploy backend
2. Deploy frontend
3. Test in production
4. Update documentation

## Expected Output

Users will see:
- Latest news for their watchlist stocks
- AI-generated summaries (3-5 sentences)
- Sentiment indicators (🟢 Bullish, 🔴 Bearish, ⚪ Neutral)
- Impact scores (High/Medium/Low)
- Source and timestamp
- Click to read full article

## Files to Create

**Backend:**
- `backend/news_service.py`
- `backend/news_summarizer_service.py`

**Frontend:**
- `frontend/src/components/NewsSection.jsx`
- `frontend/src/components/NewsSection.css`
- `frontend/src/components/NewsCard.jsx`

**Files to Modify:**
- `backend/auth_routes.py` - Add news endpoints
- `frontend/src/App.jsx` - Add news navigation

## Success Criteria

- [ ] News fetches for all watchlist stocks
- [ ] AI summaries are accurate and concise
- [ ] Sentiment analysis is reasonable
- [ ] UI is clean and readable
- [ ] Works in both light and dark modes
- [ ] Mobile responsive
- [ ] Deployed to production

## Estimated Time: 3-4 hours

## Prerequisites

- Perplexity API (already configured) ✅
- News API key (need to add to .env)
- Watchlist feature (already exists) ✅

---

## Previous Completed Features

### ✅ Account Linking (Nov 13, 2024)
- Link/unlink Google accounts
- Set primary authentication method
- Auto-linking on sign-in

### ✅ Smart Portfolio Insights (Nov 13, 2024)
- AI-powered portfolio analysis
- Diversification scoring
- Risk warnings and recommendations
- Performance tracking

---

**Ready to build!** Start by reading `AI_SESSION_CONTEXT.md` for full context.

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
