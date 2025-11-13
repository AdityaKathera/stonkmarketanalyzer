# ⚠️ CloudFront Cache Configuration - IMPORTANT

## Current Status: TEMPORARY SETTING

**CloudFront Distribution**: E2UZFZ0XAK8XWJ  
**Current Cache TTL**: 0 seconds (NO CACHING)  
**Date Changed**: November 13, 2024  
**Reason**: Faster deployments during development

## ⚠️ ACTION REQUIRED: Restore Caching After Testing

### Why This Matters

**CloudFront caching is for WEBSITE FILES (HTML, JS, CSS), NOT stock data!**

- **Website files**: HTML, JavaScript, CSS - These should be cached
- **Stock data**: Fetched from backend API - Has separate caching (1 minute)

### Current Impact

With 0 cache:
- ✅ **Good**: Instant updates when you deploy new code
- ❌ **Bad**: Every page load fetches files from S3 (slower, more expensive)
- ❌ **Bad**: Higher AWS costs (more S3 requests, more CloudFront data transfer)
- ❌ **Bad**: Slower page loads for users

### Recommended Settings

After testing is complete, restore caching:

```bash
# Recommended cache times:
- MinTTL: 0 seconds (allow immediate updates if needed)
- DefaultTTL: 3600 seconds (1 hour) - Good balance
- MaxTTL: 86400 seconds (24 hours) - Maximum cache time

# For production:
- HTML files: 300 seconds (5 minutes) - Updates quickly
- JS/CSS files: 31536000 seconds (1 year) - Files have unique hashes
- Images: 604800 seconds (1 week) - Images rarely change
```

### How to Restore Caching

#### Option 1: Quick Restore (1 hour cache)
```bash
aws cloudfront get-distribution-config --id E2UZFZ0XAK8XWJ > /tmp/cf-config.json

cat /tmp/cf-config.json | jq '.DistributionConfig | 
  .DefaultCacheBehavior.MinTTL = 0 | 
  .DefaultCacheBehavior.DefaultTTL = 3600 | 
  .DefaultCacheBehavior.MaxTTL = 86400' > /tmp/cf-config-updated.json

ETAG=$(cat /tmp/cf-config.json | jq -r '.ETag')

aws cloudfront update-distribution \
  --id E2UZFZ0XAK8XWJ \
  --distribution-config file:///tmp/cf-config-updated.json \
  --if-match $ETAG
```

#### Option 2: Optimal Production Settings
Create cache behaviors for different file types:
- `*.html` → 5 minutes
- `*.js`, `*.css` → 1 year (files have hashes in names)
- `*.png`, `*.jpg` → 1 week
- Everything else → 1 hour

### Stock Data Caching (Separate System)

Stock price caching is handled in the **backend** and is NOT affected by CloudFront:

**Location**: `backend/portfolio_service.py`
```python
# Stock prices cached for 1 minute
self.cache_expiry[ticker] = now + timedelta(minutes=1)
```

**Location**: `backend/cache_enhanced.py`
```python
# API responses cached with different TTLs
CACHE_TTL = {
    'fundamentals': 86400,  # 24 hours
    'news': 3600,           # 1 hour
    'technical': 14400,     # 4 hours
    'chat': 1800,           # 30 minutes
}
```

This backend caching is **independent** and will continue working regardless of CloudFront settings.

## Timeline

### Now (Development Phase)
- Cache TTL: 0 seconds
- Purpose: Fast iteration and testing
- Duration: Until features are tested and stable

### After Testing (Production Phase)
- Cache TTL: 1 hour (recommended)
- Purpose: Fast page loads, lower costs
- When: After Google SSO and Portfolio features are confirmed working

## Checklist

- [ ] Test Google SSO feature
- [ ] Test Enhanced Portfolio feature
- [ ] Verify all features work correctly
- [ ] **RESTORE CLOUDFRONT CACHING** (use commands above)
- [ ] Test that caching doesn't break deployments
- [ ] Monitor AWS costs

## Notes

- CloudFront changes take 5-10 minutes to propagate
- After restoring cache, use invalidations for deployments
- Consider using versioned file names (already doing this with Vite)
- Stock data caching is separate and unaffected

---

**REMEMBER**: Restore caching after testing is complete!  
**Current Status**: ⚠️ NO CACHING (Temporary)  
**Target Status**: ✅ 1 HOUR CACHING (Production)
