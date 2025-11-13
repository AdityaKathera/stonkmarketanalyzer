# 🔐 Google SSO Implementation Guide

## Overview

This guide will help you implement Google Sign-In for your Stonk Market Analyzer app.

## Prerequisites

✅ Backend Google OAuth route already exists (`/api/auth/google`)  
✅ `google-auth` library already in requirements.txt  
❌ Need Google OAuth credentials from Google Cloud Console  
❌ Need to install frontend library  
❌ Need to update AuthModal component  

## Step 1: Get Google OAuth Credentials (You Do This)

### A. Go to Google Cloud Console
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select "Stonk Market Analyzer"
3. Enable "Google+ API" or "Google Identity Services"

### B. Create OAuth 2.0 Client ID
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: "Stonk Market Analyzer Web Client"

### C. Configure Authorized Origins
Add these URLs:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
http://localhost:5173
```

### D. Configure Authorized Redirect URIs
Add these URLs:
```
https://stonkmarketanalyzer.com
https://www.stonkmarketanalyzer.com
http://localhost:5173
```

### E. Save Client ID
You'll get a Client ID like:
```
123456789-abcdefghijklmnop.apps.googleusercontent.com
```

**Save this!** You'll need it for the next steps.

## Step 2: Update Environment Variables

### Backend `.env`
Add this line:
```bash
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
```

### Frontend `.env`
Create/update `frontend/.env`:
```bash
VITE_API_URL=https://api.stonkmarketanalyzer.com
VITE_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
```

## Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install @react-oauth/google
```

## Step 4: Update AuthModal Component

I'll provide the updated code. Replace the current `AuthModal.jsx` with the enhanced version that includes Google Sign-In.

### Updated AuthModal.jsx

```javascript
import { useState } from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import './AuthModal.css';

function AuthModal({ isOpen, onClose, onSuccess }) {
  const [mode, setMode] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      setLoading(true);
      setError('');

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:3001'}/api/auth/google`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            token: credentialResponse.credential
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Google authentication failed');
      }

      // Store token and user info
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Call success callback
      onSuccess(data.user);

      // Close modal
      onClose();

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setError('Google sign-in failed. Please try again.');
  };

  // ... rest of your existing code (handleChange, validateForm, handleSubmit, etc.)

  if (!isOpen) return null;

  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <button className="modal-close" onClick={onClose}>×</button>
          
          <h2>{mode === 'login' ? 'Welcome Back' : 'Create Account'}</h2>
          <p className="modal-subtitle">
            {mode === 'login' 
              ? 'Sign in to access your portfolio' 
              : 'Start tracking your investments'}
          </p>

          {error && <div className="error-message">{error}</div>}

          {/* Google Sign-In Button */}
          <div className="google-signin-container">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap
              theme="outline"
              size="large"
              text={mode === 'login' ? 'signin_with' : 'signup_with'}
              width="100%"
            />
          </div>

          <div className="divider">
            <span>or</span>
          </div>

          {/* Rest of your existing form code */}
          <form onSubmit={handleSubmit}>
            {/* ... existing form fields ... */}
          </form>

          <div className="modal-footer">
            {mode === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button type="button" onClick={switchMode} className="link-button">
                  Sign up
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button type="button" onClick={switchMode} className="link-button">
                  Sign in
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </GoogleOAuthProvider>
  );
}

export default AuthModal;
```

### Add CSS for Google Button

Add to `AuthModal.css`:
```css
.google-signin-container {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
  color: #718096;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}

.divider span {
  padding: 0 10px;
  font-size: 14px;
}
```

## Step 5: Deploy to Production

### Deploy Backend
```bash
# Upload .env with GOOGLE_CLIENT_ID
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  backend/.env ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/

# Restart backend
ssh -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

### Deploy Frontend
```bash
cd frontend
npm run build
scp -i /Users/adityakathera/Downloads/stonkmarketanalyzer-keypair.pem \
  -r dist/* ec2-user@100.27.225.93:/var/www/stonkmarketanalyzer/
```

## Step 6: Test

### Local Testing
1. Start frontend: `npm run dev`
2. Go to `http://localhost:5173`
3. Click "Sign in with Google"
4. Select Google account
5. Should be logged in automatically

### Production Testing
1. Go to `https://stonkmarketanalyzer.com`
2. Click "Sign in with Google"
3. Select Google account
4. Should be logged in automatically

## How It Works

### Google SSO Flow
```
1. User clicks "Sign in with Google"
   ↓
2. Google popup opens
   ↓
3. User selects Google account
   ↓
4. Google returns ID token (JWT)
   ↓
5. Frontend sends token to /api/auth/google
   ↓
6. Backend verifies token with Google
   ↓
7. Backend checks if user exists
   ├─ Exists: Return existing user
   └─ New: Create account automatically
   ↓
8. Backend returns JWT token
   ↓
9. Frontend stores token
   ↓
10. User is logged in!
```

### Security Features
- ✅ Token verified with Google servers
- ✅ Email verified by Google
- ✅ No password storage for OAuth users
- ✅ Automatic account creation
- ✅ Secure JWT tokens

## Benefits

### For Users
- **Faster signup**: One click instead of form
- **No password**: Don't need to remember another password
- **Trusted**: Google's security
- **Auto-fill**: Name and email from Google

### For You
- **Higher conversion**: 50%+ more signups
- **Less support**: No password reset requests for Google users
- **Verified emails**: Google verifies emails
- **Professional**: Looks like a real app

## Troubleshooting

### "Google sign-in failed"
- Check Client ID is correct in `.env`
- Verify authorized origins in Google Console
- Check browser console for errors

### "Invalid token"
- Backend can't verify token
- Check `GOOGLE_CLIENT_ID` in backend `.env`
- Ensure `google-auth` is installed

### Button doesn't appear
- Check `VITE_GOOGLE_CLIENT_ID` in frontend `.env`
- Verify `@react-oauth/google` is installed
- Check browser console for errors

## Next Steps

1. **Get Google OAuth credentials** (Step 1)
2. **Send me the Client ID** - I'll update the code
3. **I'll implement the frontend changes**
4. **We'll test locally**
5. **Deploy to production**
6. **Test on live site**

---

**Ready to implement?** Get your Google OAuth credentials and we'll knock this out quickly!
