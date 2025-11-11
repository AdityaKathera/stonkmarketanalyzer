# Domain Name Setup Guide for Stonk Market Analyzer

This guide will help you set up a custom domain with HTTPS for full mobile support.

## Step 1: Purchase a Domain Name

### Option A: AWS Route 53 (Easiest)
1. Go to AWS Console → Route 53 → Registered domains
2. Click "Register domain"
3. Search for available domains (e.g., `stonkanalyzer.com`, `mystonkapp.com`)
4. Cost: ~$12-15/year for .com domains
5. Complete registration (takes 10-30 minutes)

### Option B: External Registrar (Namecheap, GoDaddy, etc.)
1. Go to Namecheap.com or GoDaddy.com
2. Search and purchase a domain
3. Cost: ~$10-15/year
4. You'll need to configure nameservers later

## Step 2: Configure DNS

### If using Route 53:
DNS is automatically configured. Skip to Step 3.

### If using external registrar:
1. Create a hosted zone in Route 53:
   ```bash
   aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)
   ```
2. Note the nameservers from the output
3. Go to your domain registrar's DNS settings
4. Update nameservers to the Route 53 nameservers
5. Wait 24-48 hours for propagation (usually faster)

## Step 3: Point Domain to Your Resources

Once you have a domain, run our automated setup script:

```bash
./deployment/setup-domain.sh yourdomain.com
```

This script will:
1. Create DNS records pointing to your EC2 and CloudFront
2. Request SSL certificate from Let's Encrypt
3. Configure nginx with HTTPS
4. Update CloudFront with custom domain
5. Update frontend to use new domain

## Step 4: Test Your Application

After setup completes:
- **Frontend**: https://yourdomain.com
- **Backend API**: https://api.yourdomain.com

Test on mobile devices - it should work perfectly!

## Recommended Domain Names

Good options for your app:
- stonkanalyzer.com
- stonkmarketai.com
- mystonkapp.com
- aistock.app
- stonkresearch.com
- stockcopilot.ai

## Cost Summary

- Domain registration: $12-15/year
- Route 53 hosted zone: $0.50/month
- SSL certificate: FREE (Let's Encrypt)
- **Total: ~$12-20/year**

## What Happens After Domain Setup

✅ Full HTTPS on both frontend and backend
✅ Works on all mobile devices
✅ Professional custom URL
✅ Automatic SSL certificate renewal
✅ Better SEO and trust

## Timeline

- Domain purchase: Instant
- DNS propagation: 10 minutes - 48 hours (usually < 1 hour)
- SSL certificate: 2-5 minutes
- Total setup time: 15-30 minutes (after domain is ready)

## Next Steps

1. Purchase a domain (Step 1)
2. Come back with your domain name
3. Run: `./deployment/setup-domain.sh yourdomain.com`
4. Wait 5-10 minutes
5. Access your app at https://yourdomain.com

---

**Once you have a domain, let me know and I'll help you complete the setup!**
