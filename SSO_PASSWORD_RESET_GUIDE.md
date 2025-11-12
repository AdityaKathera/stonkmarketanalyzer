# 🔐 SSO & Password Reset Implementation Guide

## ✅ What's Been Added

### 1. Password Reset Functionality
- **Email From**: `password-reset@stonkmarketanalyzer.com`
- **Token Expiry**: 1 hour
- **Security**: One-time use tokens
- **Email Template**: Professional HTML email with reset link

### 2. Google OAuth SSO
- **Provider**: Google Sign-In
- **Flow**: OAuth 2.0
- **Auto-Registration**: Creates account if new user
- **Seamless**: No password needed for Google users

---

## 📁 Files Created

### Backend:
1. `backend/password_reset_service.py` - Password reset logic
2. Updated `backend/auth_routes.py` - New endpoints
3. Updated `backend/requirements.txt` - Added boto3, google-auth

### Frontend:
1. `frontend/src/components/ForgotPassword.jsx` - Forgot password modal
2. `frontend/src/components/ForgotPassword.css` - Styling
3. `frontend/src/components/ResetPassword.jsx` - Reset password page
4. `frontend/src/components/ResetPassword.css` - Styling

---

## 🚀 Setup Instructions

### Step 1: Verify SES Email Address

The email `password-reset@stonkmarketanalyzer.com` needs to be verified in AWS SES:

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=$(cat /tmp/role-creds.json | grep AccessKeyId | cut -d'"' -f4)
export AWS_SECRET_ACCESS_KEY=$(cat /tmp/role-creds.json | grep SecretAccessKey | cut -d'"' -f4)
export AWS_SESSION_TOKEN=$(cat /tmp/role-creds.json | grep SessionToken | cut -d'"' -f4)

# Verify email address
aws ses verify-email-identity \
  --email-address password-reset@stonkmarketanalyzer.com \
  --region us-east-1

# Check verification status
aws ses get-identity-verification-attributes \
  --identities password-reset@stonkmarketanalyzer.com \
  --region us-east-1
```

**Note**: Since your domain `stonkmarketanalyzer.com` is already verified, any email @stonkmarketanalyzer.com should work automatically!

---

### Step 2: Set Up Google OAuth

#### A. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized JavaScript origins:
   - `https://stonkmarketanalyzer.com`
   - `https://www.stonkmarketanalyzer.com`
   - `http://localhost:5173` (for development)
7. Authorized redirect URIs:
   - `https://stonkmarketanalyzer.com`
   - `https://www.stonkmarketanalyzer.com`
8. Copy the **Client ID**

#### B. Add to Backend Environment

```bash
# SSH into EC2
ssh -i key.pem ec2-user@100.27.225.93

# Add to .env
echo "GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com" >> /home/ec2-user/backend/.env
echo "FRONTEND_URL=https://stonkmarketanalyzer.com" >> /home/ec2-user/backend/.env
```

#### C. Add to Frontend Environment

```bash
# In frontend/.env
echo "VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com" >> frontend/.env
```

---

### Step 3: Install Dependencies

#### Backend:
```bash
# SSH into EC2
ssh -i key.pem ec2-user@100.27.225.93

cd /home/ec2-user/backend
pip3 install --user boto3==1.34.0
pip3 install --user google-auth==2.25.2

# Restart backend
pkill -9 -f 'python3 app.py'
nohup python3 app.py > app.log 2>&1 &
```

#### Frontend:
```bash
# Install Google Sign-In library
npm install --prefix frontend @react-oauth/google
```

---

### Step 4: Update Frontend Components

#### A. Update AuthModal.jsx

Add these imports at the top:
```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import ForgotPassword from './ForgotPassword';
```

Add state for forgot password modal:
```javascript
const [showForgotPassword, setShowForgotPassword] = useState(false);
```

Add Google login handler:
```javascript
const handleGoogleSuccess = async (credentialResponse) => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: credentialResponse.credential }),
    });

    const data = await response.json();
    if (response.ok) {
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      onSuccess(data.user);
      onClose();
    }
  } catch (error) {
    setError('Google sign-in failed');
  }
};
```

Add to the form (after password field for login mode):
```javascript
{mode === 'login' && (
  <div className="forgot-password-link">
    <button 
      type="button" 
      onClick={() => setShowForgotPassword(true)}
      className="link-btn"
    >
      Forgot password?
    </button>
  </div>
)}

<div className="divider">
  <span>OR</span>
</div>

<GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
  <GoogleLogin
    onSuccess={handleGoogleSuccess}
    onError={() => setError('Google sign-in failed')}
    useOneTap
  />
</GoogleOAuthProvider>

<ForgotPassword 
  isOpen={showForgotPassword}
  onClose={() => setShowForgotPassword(false)}
/>
```

#### B. Update App.jsx

Add routing for reset password page:
```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ResetPassword from './components/ResetPassword';

// Wrap your app with BrowserRouter and add route
<BrowserRouter>
  <Routes>
    <Route path="/reset-password" element={<ResetPassword />} />
    <Route path="/" element={<YourMainApp />} />
  </Routes>
</BrowserRouter>
```

---

## 🧪 Testing

### Test Password Reset:

1. **Request Reset**:
```bash
curl -X POST https://api.stonkmarketanalyzer.com/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

2. **Check Email**: Look for email from `password-reset@stonkmarketanalyzer.com`

3. **Verify Token**:
```bash
curl -X POST https://api.stonkmarketanalyzer.com/api/auth/verify-reset-token \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token-here"}'
```

4. **Reset Password**:
```bash
curl -X POST https://api.stonkmarketanalyzer.com/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token-here","password":"newpassword123"}'
```

### Test Google OAuth:

1. Go to https://stonkmarketanalyzer.com
2. Click "Sign In"
3. Click "Sign in with Google"
4. Select Google account
5. Should be logged in automatically

---

## 📊 New API Endpoints

### Password Reset:
```
POST /api/auth/forgot-password
Body: { "email": "user@example.com" }
Response: { "success": true, "message": "..." }

POST /api/auth/verify-reset-token
Body: { "token": "..." }
Response: { "valid": true }

POST /api/auth/reset-password
Body: { "token": "...", "password": "newpass" }
Response: { "success": true, "message": "..." }
```

### Google OAuth:
```
POST /api/auth/google
Body: { "token": "google-id-token" }
Response: { "success": true, "token": "jwt-token", "user": {...} }
```

---

## 🔒 Security Features

### Password Reset:
- ✅ Tokens expire after 1 hour
- ✅ One-time use only
- ✅ Secure random token generation
- ✅ Email enumeration prevention
- ✅ Rate limiting (recommended to add)

### Google OAuth:
- ✅ Token verification with Google
- ✅ Secure user creation
- ✅ No password storage for OAuth users
- ✅ Email verification via Google

---

## 💰 Cost

### AWS SES:
- **Free Tier**: 62,000 emails/month
- **After Free Tier**: $0.10 per 1,000 emails
- **Your Usage**: ~10-50 password resets/month = **FREE**

### Google OAuth:
- **Cost**: FREE (unlimited)
- **No API limits** for basic authentication

**Total Additional Cost**: $0/month

---

## 🎨 UI/UX Flow

### Password Reset Flow:
1. User clicks "Forgot Password?" on login
2. Modal opens asking for email
3. User enters email and submits
4. Success message shown
5. User receives email with reset link
6. User clicks link → Redirected to reset page
7. User enters new password
8. Success → Redirected to home
9. User can login with new password

### Google SSO Flow:
1. User clicks "Sign in with Google"
2. Google popup opens
3. User selects account
4. Auto-logged in
5. If new user → Account created automatically
6. Redirected to app (logged in)

---

## 📧 Email Template Preview

**Subject**: Reset Your Password - Stonk Market Analyzer

**Body**:
```
Hi [Name],

You requested to reset your password for Stonk Market Analyzer.

[Reset Password Button]

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Stonk Market Analyzer Team
```

---

## 🚀 Deployment Checklist

- [ ] Verify `password-reset@stonkmarketanalyzer.com` in SES
- [ ] Create Google OAuth credentials
- [ ] Add `GOOGLE_CLIENT_ID` to backend .env
- [ ] Add `VITE_GOOGLE_CLIENT_ID` to frontend .env
- [ ] Install backend dependencies (boto3, google-auth)
- [ ] Install frontend dependencies (@react-oauth/google)
- [ ] Update AuthModal component
- [ ] Add routing for reset password page
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Test password reset flow
- [ ] Test Google OAuth flow

---

## 🐛 Troubleshooting

### Email Not Received:
- Check spam folder
- Verify SES email address
- Check SES sending limits
- Review CloudWatch logs

### Google OAuth Not Working:
- Verify Client ID is correct
- Check authorized origins
- Ensure HTTPS is used
- Check browser console for errors

### Token Expired:
- Tokens expire after 1 hour
- Request new reset link
- Check server time is correct

---

## 📚 Next Steps

1. **Deploy the changes** (see deployment section below)
2. **Test both features** thoroughly
3. **Monitor email delivery** in SES console
4. **Add rate limiting** to prevent abuse
5. **Consider adding**:
   - Facebook/Twitter OAuth
   - 2FA (Two-Factor Authentication)
   - Email verification for new signups

---

## 🎉 Benefits

### For Users:
- ✅ Can reset forgotten passwords easily
- ✅ Quick sign-up with Google (no password needed)
- ✅ Professional email experience
- ✅ Secure and reliable

### For You:
- ✅ Reduced support requests ("I forgot my password")
- ✅ Higher conversion (easier sign-up with Google)
- ✅ Better security
- ✅ Professional image

---

**All code is ready! Just need to deploy and configure Google OAuth credentials.**
