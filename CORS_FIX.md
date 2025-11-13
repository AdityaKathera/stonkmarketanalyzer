# CORS Fix - Profile Update Error

## Issue
**Error**: `Access to fetch at 'https://api.stonkmarketanalyzer.com/api/auth/profile' from origin 'https://www.stonkmarketanalyzer.com' has been blocked by CORS policy: Method PUT is not allowed by Access-Control-Allow-Methods in preflight response.`

**Status Code**: 403 Forbidden

**Affected Features**:
- Update profile name
- Change password

## Root Cause
The Nginx configuration was only allowing `GET, POST, OPTIONS` methods in the CORS preflight response, but the new profile endpoints use `PUT` and `POST` methods.

## Solution

### 1. Updated Flask CORS Configuration
**File**: `backend/app.py`

```python
# Before
CORS(app, origins=allowed_origins)

# After
CORS(app, 
     origins=allowed_origins,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)
```

### 2. Updated Nginx Configuration
**File**: `/etc/nginx/conf.d/stonkmarketanalyzer.conf`

```nginx
# Before
add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;

# After
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
```

## Deployment Steps

1. **Update Flask app**:
```bash
scp backend/app.py ec2-user@100.27.225.93:/opt/stonkmarketanalyzer/backend/
ssh ec2-user@100.27.225.93 "bash /tmp/restart-backend-remote.sh"
```

2. **Update Nginx config**:
```bash
ssh ec2-user@100.27.225.93 "sudo sed -i 's/Access-Control-Allow-Methods \"GET, POST, OPTIONS\"/Access-Control-Allow-Methods \"GET, POST, PUT, DELETE, OPTIONS\"/g' /etc/nginx/conf.d/stonkmarketanalyzer.conf"
ssh ec2-user@100.27.225.93 "sudo nginx -t"
ssh ec2-user@100.27.225.93 "sudo systemctl reload nginx"
```

## Verification

### Test CORS Preflight
```bash
curl -X OPTIONS https://api.stonkmarketanalyzer.com/api/auth/profile \
  -H "Origin: https://www.stonkmarketanalyzer.com" \
  -H "Access-Control-Request-Method: PUT" \
  -v 2>&1 | grep -i "allow-methods"
```

**Expected Output**:
```
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
```

### Test Profile Update
1. Go to https://stonkmarketanalyzer.com
2. Login to your account
3. Click "⚙️ Profile"
4. Update your name
5. Click "Save Changes"
6. Should see success message ✅

### Test Password Change
1. Go to Profile → Security tab
2. Enter current password
3. Enter new password
4. Click "Change Password"
5. Should see success message ✅

## Technical Details

### CORS Preflight Request
When the browser makes a PUT request, it first sends an OPTIONS request (preflight) to check if the server allows it:

```
OPTIONS /api/auth/profile HTTP/1.1
Origin: https://www.stonkmarketanalyzer.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: content-type, authorization
```

The server must respond with:
```
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Why Both Flask and Nginx?
- **Flask**: Handles CORS for direct API calls
- **Nginx**: Acts as reverse proxy and can override/add headers
- **Both needed**: Nginx was intercepting and overriding Flask's CORS headers

## Status
✅ **Fixed and Deployed** - November 13, 2024, 7:35 AM UTC

## Affected Endpoints
- `PUT /api/auth/profile` - Update user name
- `POST /api/auth/change-password` - Change password
- Any future PUT/DELETE endpoints

## Prevention
For future endpoints using PUT or DELETE methods, they will now work automatically since CORS is configured to allow all standard HTTP methods.

---

**Issue**: CORS 403 error on profile update  
**Fix**: Added PUT/DELETE to CORS allowed methods  
**Status**: ✅ Resolved and deployed
