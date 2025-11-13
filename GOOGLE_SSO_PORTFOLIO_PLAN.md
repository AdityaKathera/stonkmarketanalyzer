# 🚀 Google SSO & Enhanced Portfolio Implementation Plan

## Phase 1: Google SSO (Priority 1)

### What We Have
✅ Backend Google OAuth route (`/api/auth/google`)  
✅ Google auth library in requirements.txt  
✅ Basic auth flow structure  

### What We Need
❌ Google OAuth credentials from Google Cloud Console  
❌ Frontend Google Sign-In button  
❌ Environment variables configured  
❌ Testing and deployment  

### Implementation Steps

#### Step 1: Get Google OAuth Credentials (5 min)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project "Stonk Market Analyzer"
3. Enable Google+ API
4. Create OAuth 2.0 Client ID
5. Add authorized origins:
   - `https://stonkmarketanalyzer.com`
   - `https://www.stonkmarketanalyzer.com`
   - `http://localhost:5173` (for development)
6. Add authorized redirect URIs:
   - `https://stonkmarketanalyzer.com`
   - `http://localhost:5173`

#### Step 2: Update Environment Variables
**Backend (.env)**:
```
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

**Frontend (.env)**:
```
VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

#### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install @react-oauth/google
```

#### Step 4: Update AuthModal Component
- Add Google Sign-In button
- Handle Google OAuth response
- Store token and user info

#### Step 5: Test & Deploy
- Test locally
- Deploy to production
- Verify on live site

---

## Phase 2: Enhanced Portfolio (Priority 2)

### Current Features
✅ Add stocks manually  
✅ View holdings  
✅ Delete holdings  
✅ Basic info (shares, purchase price, date)  

### New Features to Add

#### 2.1 Real-Time Portfolio Value (High Priority)
- Fetch current stock prices
- Calculate current value vs cost basis
- Show total P&L (profit/loss)
- Show P&L percentage
- Color coding (green for profit, red for loss)

#### 2.2 Portfolio Summary Dashboard
- Total portfolio value
- Total cost basis
- Total P&L ($)
- Total P&L (%)
- Best performer
- Worst performer
- Pie chart of holdings

#### 2.3 Individual Stock Performance
- Current price
- Day change
- Total return ($)
- Total return (%)
- Unrealized gain/loss

#### 2.4 Portfolio Analytics
- Sector allocation
- Risk score
- Diversification score
- Dividend yield (if applicable)

#### 2.5 Historical Performance
- Portfolio value over time
- Line chart showing growth
- Compare to S&P 500

### Implementation Steps

#### Step 1: Backend - Portfolio API Enhancements
Create new endpoints:
- `GET /api/portfolio/summary` - Get portfolio summary with current prices
- `GET /api/portfolio/performance` - Get historical performance
- `PATCH /api/portfolio/:id` - Update holding

#### Step 2: Frontend - Enhanced Portfolio Component
- Add real-time price fetching
- Add summary cards
- Add performance charts
- Add edit functionality

#### Step 3: Database Schema Updates
Add columns to portfolio table:
- `current_price` (cached)
- `last_updated` (timestamp)
- `sector` (optional)

---

## Implementation Order

### Week 1: Google SSO
**Day 1-2**: Setup & Backend
- Get Google OAuth credentials
- Configure environment variables
- Test backend endpoint

**Day 3-4**: Frontend Integration
- Install dependencies
- Update AuthModal
- Test login flow

**Day 5**: Deploy & Test
- Deploy to production
- Test on live site
- Monitor for issues

### Week 2: Enhanced Portfolio
**Day 1-2**: Backend APIs
- Create portfolio summary endpoint
- Add real-time price fetching
- Add performance calculations

**Day 3-4**: Frontend UI
- Build summary dashboard
- Add performance metrics
- Add charts

**Day 5**: Polish & Deploy
- Add loading states
- Error handling
- Deploy to production

---

## Technical Details

### Google SSO Flow
```
1. User clicks "Sign in with Google"
2. Google popup opens
3. User selects Google account
4. Google returns ID token
5. Frontend sends token to backend
6. Backend verifies token with Google
7. Backend creates/finds user
8. Backend returns JWT token
9. Frontend stores token
10. User is logged in
```

### Portfolio Value Calculation
```javascript
// For each holding:
currentValue = shares * currentPrice
costBasis = shares * purchasePrice
unrealizedGain = currentValue - costBasis
returnPercentage = (unrealizedGain / costBasis) * 100

// Portfolio totals:
totalValue = sum(all currentValues)
totalCost = sum(all costBases)
totalGain = totalValue - totalCost
totalReturn = (totalGain / totalCost) * 100
```

---

## Success Metrics

### Google SSO
- ✅ 50%+ of new users sign up with Google
- ✅ Reduced signup friction
- ✅ Lower bounce rate on signup

### Enhanced Portfolio
- ✅ Users add 3+ stocks on average
- ✅ Users check portfolio daily
- ✅ Increased session duration
- ✅ Higher user retention

---

## Next Steps

1. **Get Google OAuth credentials** (you need to do this)
2. **I'll implement the frontend Google SSO**
3. **I'll enhance the portfolio with real-time data**
4. **We'll test and deploy**

Ready to start? Let me know when you have the Google OAuth credentials!
