# Floating Chat - Debug Guide

## Status
✅ Backend endpoint created (`/api/chat`)  
✅ Frontend component created  
❌ API calls not reaching backend (needs debugging)

## Issue
Chat shows fallback error: "I'm having trouble connecting right now"

## Debugging Steps

### 1. Check Browser Console
Open browser console (F12) and look for:
```
[FloatingChat] Sending message to API: ...
[FloatingChat] API response status: ...
```

### 2. Check for JavaScript Errors
Look for any red errors in console that might be preventing the API call.

### 3. Check Network Tab
- Open DevTools → Network tab
- Send a chat message
- Look for POST request to `/api/chat`
- Check if request is made and what the response is

### 4. Test API Directly
```bash
# Get a valid token by logging in, then:
curl -X POST https://api.stonkmarketanalyzer.com/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","context":{}}'
```

### 5. Check Backend Logs
```bash
ssh -i ~/.ssh/key.pem ec2-user@100.27.225.93 \
  "tail -f /opt/stonkmarketanalyzer/backend/backend.log | grep chat"
```

## Possible Issues

### Issue 1: CloudFront Cache
**Solution**: Wait 5-10 minutes for cache to clear, or:
```bash
aws cloudfront create-invalidation \
  --distribution-id E2UZFZ0XAK8XWJ \
  --paths "/*"
```

### Issue 2: Missing datetime Import
The backend endpoint uses `datetime.now()` but might not have imported it.

**Fix**: Add to backend/auth_routes.py:
```python
from datetime import datetime
```

### Issue 3: CORS Issue
If you see CORS errors in console.

**Fix**: Check that POST is allowed in CORS config.

## Quick Fix: Use Old ChatInterface

If debugging takes too long, you can temporarily revert:

1. Add Chat tab back to navigation
2. Keep FloatingChat for later
3. Use the working ChatInterface component

## Files Involved

**Backend:**
- `backend/auth_routes.py` - Chat endpoint (line ~750)

**Frontend:**
- `frontend/src/components/FloatingChat.jsx` - Chat component
- `frontend/src/components/FloatingChat.css` - Styling
- `frontend/src/App.jsx` - Integration

## Next Steps

1. Hard refresh browser (Cmd+Shift+R)
2. Check console for errors
3. Try sending a message
4. Check network tab for API call
5. If no API call, check for JavaScript errors
6. If API call fails, check response status/error

## Contact
The floating chat UI is complete and beautiful. Just needs the API connection debugged. Should be a quick fix once we see the actual error in console!
