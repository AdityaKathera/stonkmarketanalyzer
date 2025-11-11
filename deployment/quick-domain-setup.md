# Quick Domain Setup - Step by Step

## What You Need
- A domain name (we'll help you get one)
- 15-30 minutes
- ~$12-15 for the domain

## Step-by-Step Process

### 1. Buy a Domain (Choose One Method)

#### Method A: AWS Route 53 (Recommended - Easiest)
```bash
# Open AWS Console
# Go to: Route 53 → Registered domains → Register domain
# Search for: stonkanalyzer.com (or your preferred name)
# Complete purchase (~$12-15/year)
# Wait 10-30 minutes for registration
```

#### Method B: Namecheap (Cheaper)
```bash
# Go to: https://www.namecheap.com
# Search for domain
# Purchase (~$10/year)
# You'll configure DNS later
```

### 2. Wait for Domain to be Ready
- Route 53: 10-30 minutes
- External registrar: Instant purchase, but DNS takes 24-48 hours

### 3. Run Our Setup Script

Once your domain is ready:

```bash
chmod +x deployment/setup-domain.sh
./deployment/setup-domain.sh yourdomain.com
```

Replace `yourdomain.com` with your actual domain.

### 4. Follow the Prompts

The script will:
1. ✅ Create DNS records automatically
2. ✅ Install SSL certificate (free from Let's Encrypt)
3. ✅ Configure HTTPS on backend
4. ⚠️ Ask you to configure CloudFront (manual step)
5. ✅ Deploy updated frontend

### 5. Manual CloudFront Step

When prompted, do this:

1. Open AWS Console → CloudFront
2. Click on distribution `E2UZFZ0XAK8XWJ`
3. Click "Edit"
4. Under "Alternate domain names (CNAMEs)", add your domain
5. Under "Custom SSL certificate":
   - Click "Request certificate"
   - Enter your domain name
   - Validate via DNS (automatic if using Route 53)
   - Wait 5-10 minutes for certificate
   - Select the certificate
6. Click "Save changes"
7. Go back to terminal and press Enter

### 6. Test Your App

After 5-10 minutes:
- Visit: https://yourdomain.com
- Test on mobile: Should work perfectly!
- Test API: https://api.yourdomain.com/api/health

## Recommended Domain Names

Available and good for your app:
- stonkanalyzer.com
- stonkmarketai.com  
- mystonkapp.com
- aistock.app
- stonkresearch.io
- stockcopilot.ai

## Costs

- Domain: $12-15/year
- Route 53 DNS: $0.50/month
- SSL: FREE (Let's Encrypt)
- **Total: ~$18/year**

## Troubleshooting

**Domain not working yet?**
- Wait 10-60 minutes for DNS propagation
- Check: `dig yourdomain.com`

**SSL certificate failed?**
- Make sure DNS is pointing to EC2
- Wait a few minutes and try again
- Check: `curl http://api.yourdomain.com`

**CloudFront not working?**
- Make sure you added the domain to CNAMEs
- Make sure SSL certificate is validated
- Wait 10-15 minutes for CloudFront to deploy

## What You Get

✅ Professional custom domain
✅ Full HTTPS everywhere
✅ Works on all mobile devices
✅ Auto-renewing SSL certificates
✅ Better SEO and credibility

---

**Ready to start? Purchase a domain and run the setup script!**
