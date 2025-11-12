# 🔐 Authentication & Portfolio Setup Guide

## ✅ What's Been Added

### Backend Features:
1. **User Authentication System**
   - Sign-up with email/password
   - Login with JWT tokens
   - Secure password hashing with bcrypt
   - Session management

2. **Portfolio Management**
   - Add stocks to portfolio (ticker, shares, purchase price, date)
   - View all holdings
   - Update holdings
   - Delete holdings
   - Notes for each holding

3. **Database Tables**
   - `users` - User accounts
   - `portfolio` - User stock holdings
   - `watchlist` - User watchlist (ready for future use)

### Frontend Features:
1. **Authentication Modal**
   - Beautiful sign-up/login UI
   - Form validation
   - Error handling
   - Smooth animations

2. **Portfolio Component**
   - Add stocks with purchase details
   - View portfolio grid
   - Delete holdings
   - Empty state with call-to-action

3. **User Menu**
   - Display logged-in user
   - Logout functionality
   - Portfolio tab (only visible when logged in)

## 🚀 Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip3 install bcrypt==4.1.2
# or if using virtual environment:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Add to `backend/.env`:
```bash
JWT_SECRET=your-super-secret-jwt-key-here-change-this
SESSION_SECRET=your-session-secret-here
```

Generate secure secrets:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start Backend

```bash
cd backend
python3 app.py
```

The database (`users.db`) will be created automatically on first run.

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Test the Features

1. **Sign Up**:
   - Click "Sign In" button in header
   - Switch to "Sign up" tab
   - Enter name, email, password
   - Create account

2. **Add to Portfolio**:
   - Click "Portfolio" tab (appears after login)
   - Click "+ Add Stock"
   - Fill in stock details
   - Submit

3. **View Portfolio**:
   - See all your holdings in a grid
   - Each card shows shares, purchase price, total cost, date
   - Delete holdings with trash icon

## 🔒 Security Features

### Password Security:
- Minimum 8 characters required
- Hashed with bcrypt (industry standard)
- Never stored in plain text

### JWT Tokens:
- 7-day expiration
- Stored in localStorage
- Sent with every authenticated request
- Verified on backend for each protected route

### API Protection:
- `@require_auth` decorator on protected routes
- Token validation on every request
- User ownership verification for portfolio operations

## 📁 File Structure

```
backend/
├── auth_service.py       # Authentication logic & database
├── auth_routes.py        # API endpoints for auth & portfolio
├── app.py               # Main app (updated with auth blueprint)
├── users.db             # SQLite database (auto-created)
└── requirements.txt     # Updated with bcrypt

frontend/
├── src/
│   ├── components/
│   │   ├── AuthModal.jsx      # Sign-up/Login modal
│   │   ├── AuthModal.css      # Modal styles
│   │   ├── Portfolio.jsx      # Portfolio management
│   │   └── Portfolio.css      # Portfolio styles
│   ├── App.jsx                # Updated with auth state
│   └── App.css                # Updated with user menu styles
```

## 🎯 API Endpoints

### Authentication:
- `POST /api/auth/signup` - Create new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (requires auth)

### Portfolio:
- `GET /api/portfolio` - Get user's portfolio (requires auth)
- `POST /api/portfolio` - Add stock to portfolio (requires auth)
- `PUT /api/portfolio/:id` - Update holding (requires auth)
- `DELETE /api/portfolio/:id` - Delete holding (requires auth)

### Watchlist (Ready for future):
- `GET /api/watchlist` - Get user's watchlist (requires auth)
- `POST /api/watchlist` - Add to watchlist (requires auth)
- `DELETE /api/watchlist/:id` - Remove from watchlist (requires auth)

## 🧪 Testing

### Test Sign-up:
```bash
curl -X POST http://localhost:3001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
```

### Test Login:
```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Portfolio (with token):
```bash
curl -X GET http://localhost:3001/api/portfolio \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## 🎨 UI/UX Features

### Authentication Modal:
- Smooth slide-in animation
- Dark mode support
- Form validation with error messages
- Loading states
- Easy toggle between sign-up/login

### Portfolio:
- Responsive grid layout
- Empty state with call-to-action
- Smooth animations
- Delete confirmation
- Dark mode support
- Mobile-friendly

### Header:
- User menu with name/email
- Logout button
- Portfolio tab (conditional)
- Consistent styling

## 🔄 User Flow

1. **New User**:
   - Lands on site → Can use all features without login
   - Clicks "Sign In" → Modal opens
   - Switches to "Sign up" → Creates account
   - Automatically logged in → Token stored
   - "Portfolio" tab appears → Can start tracking

2. **Returning User**:
   - Lands on site → Token auto-loaded from localStorage
   - Already logged in → Portfolio tab visible
   - Can immediately access portfolio

3. **Logout**:
   - Clicks "Logout" → Token removed
   - Portfolio tab disappears
   - Can still use other features

## 🚧 Future Enhancements (Not Implemented Yet)

1. **Email Verification**
   - Send verification email on sign-up
   - Verify email before full access

2. **Password Reset**
   - "Forgot password" link
   - Email reset link
   - Secure token-based reset

3. **Social Login**
   - Google OAuth
   - GitHub OAuth

4. **Portfolio Analytics**
   - Real-time stock prices
   - Profit/loss calculations
   - Performance charts
   - Benchmark comparisons

5. **Watchlist Integration**
   - Add stocks to watchlist
   - Price alerts
   - News notifications

## 📊 Database Schema

### users table:
```sql
id INTEGER PRIMARY KEY
email TEXT UNIQUE NOT NULL
password_hash TEXT NOT NULL
name TEXT
created_at TIMESTAMP
last_login TIMESTAMP
email_verified BOOLEAN DEFAULT 1
```

### portfolio table:
```sql
id INTEGER PRIMARY KEY
user_id INTEGER (FK to users)
ticker TEXT NOT NULL
shares REAL NOT NULL
purchase_price REAL NOT NULL
purchase_date DATE NOT NULL
notes TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
UNIQUE(user_id, ticker, purchase_date)
```

### watchlist table:
```sql
id INTEGER PRIMARY KEY
user_id INTEGER (FK to users)
ticker TEXT NOT NULL
added_at TIMESTAMP
notes TEXT
UNIQUE(user_id, ticker)
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'bcrypt'"
```bash
pip3 install bcrypt==4.1.2
```

### "ModuleNotFoundError: No module named 'jwt'"
```bash
pip3 install pyjwt==2.8.0
```

### Database locked error:
```bash
# Stop backend, delete users.db, restart
rm backend/users.db
python3 backend/app.py
```

### Token expired:
- Logout and login again
- Token expires after 7 days

### CORS errors:
- Make sure backend is running on port 3001
- Check ALLOWED_ORIGINS in backend/.env

## ✅ Deployment Checklist

Before deploying to production:

1. ✅ Change JWT_SECRET to a strong random value
2. ✅ Change SESSION_SECRET to a strong random value
3. ✅ Use PostgreSQL instead of SQLite for production
4. ✅ Enable HTTPS
5. ✅ Set secure cookie flags
6. ✅ Add rate limiting
7. ✅ Add email verification
8. ✅ Add password reset
9. ✅ Add 2FA (optional)
10. ✅ Add logging and monitoring

## 🎉 Success!

You now have a fully functional authentication system with portfolio management! Users can:
- ✅ Sign up and login securely
- ✅ Track their stock holdings
- ✅ View their portfolio
- ✅ Add/remove stocks
- ✅ All data is private and secure

Next steps: Deploy to AWS and start adding more features!
