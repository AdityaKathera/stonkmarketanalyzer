# Android App - Test & Release Guide

Quick guide to test your app and publish to Google Play Store.

---

## Part 1: Testing in Android Studio (30 minutes)

### Step 1: Open Project

```bash
cd frontend
npx cap open android
```

Android Studio will open with your project.

### Step 2: Set Up Emulator

1. In Android Studio, click the device dropdown (top toolbar)
2. Click "Device Manager"
3. Click "Create Device"
4. Select "Pixel 5" (or any phone)
5. Click "Next"
6. Download a system image (recommend "Tiramisu" - API 33)
7. Click "Next" → "Finish"

### Step 3: Run the App

1. Make sure your emulator is selected in the device dropdown
2. Click the green "Run" button (▶️) or press `Ctrl+R`
3. Wait for app to build and launch (2-3 minutes first time)
4. App will open in the emulator!

### Step 4: Test Everything

Test these features:
- [ ] App launches without crashes
- [ ] Enter a stock ticker (e.g., AAPL)
- [ ] Run "Business Overview" analysis
- [ ] Try Chat mode
- [ ] Try Stock Comparison
- [ ] Add stock to Watchlist
- [ ] Toggle dark mode
- [ ] Rotate screen (works in both orientations?)

**If anything doesn't work, let me know!**

---

## Part 2: Prepare for Release (1 hour)

### Step 1: Create App Icon

1. Go to https://icon.kitchen
2. Upload your logo or create one:
   - Use 🚀📊 emojis
   - Simple design
   - High contrast
3. Download the icon pack
4. In Android Studio:
   - Right-click `app/src/main/res`
   - Select "New" → "Image Asset"
   - Choose "Launcher Icons"
   - Upload your icon
   - Click "Next" → "Finish"

### Step 2: Update App Info

Open `android/app/build.gradle` and update:

```gradle
android {
    defaultConfig {
        applicationId "com.adityakathera.stonkanalyzer"
        minSdkVersion 22
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
    }
}
```

### Step 3: Create Signing Key

Open Terminal and run:

```bash
cd ~/Desktop
keytool -genkey -v -keystore stonk-release-key.keystore -alias stonk-key -keyalg RSA -keysize 2048 -validity 10000
```

Answer the prompts:
- **Password:** [Create a strong password - SAVE THIS!]
- **Re-enter password:** [Same password]
- **First and last name:** Aditya Kathera
- **Organizational unit:** [Press Enter]
- **Organization:** [Press Enter]
- **City:** [Your city]
- **State:** [Your state]
- **Country code:** US (or your country)
- **Is this correct?** yes

**CRITICAL:** Save this file and password! You'll need it for ALL future updates.

Move the keystore to your project:
```bash
mv ~/Desktop/stonk-release-key.keystore ~/Desktop/stonkmarketanalyzer/
```

### Step 4: Configure Signing in Project

Create `android/key.properties`:

```bash
cd ~/Desktop/stonkmarketanalyzer/frontend/android
cat > key.properties << 'EOF'
storePassword=YOUR_PASSWORD_HERE
keyPassword=YOUR_PASSWORD_HERE
keyAlias=stonk-key
storeFile=../../stonk-release-key.keystore
EOF
```

Replace `YOUR_PASSWORD_HERE` with your actual password.

Update `android/app/build.gradle` - add this BEFORE `android {`:

```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    // ... existing config ...
    
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

---

## Part 3: Build Release APK/AAB (15 minutes)

### Option A: Build AAB (Recommended for Play Store)

In Android Studio:
1. Go to `Build` → `Generate Signed Bundle / APK`
2. Select "Android App Bundle"
3. Click "Next"
4. Key store path: Browse to `stonk-release-key.keystore`
5. Enter your password
6. Key alias: `stonk-key`
7. Click "Next"
8. Select "release" build variant
9. Click "Finish"

**Output:** `android/app/build/outputs/bundle/release/app-release.aab`

### Option B: Build APK (For testing)

```bash
cd frontend/android
./gradlew assembleRelease
```

**Output:** `android/app/build/outputs/apk/release/app-release.apk`

---

## Part 4: Register Google Play Developer Account (30 minutes)

### Step 1: Sign Up

1. Go to https://play.google.com/console/signup
2. Sign in with your Google account
3. Click "Continue to account setup"
4. Choose "Individual" account type
5. Fill in your details:
   - Developer name: Aditya Kathera (or your name)
   - Email: [Your email]
   - Phone: [Your phone]
6. Pay $25 registration fee
7. Accept Developer Distribution Agreement
8. Complete identity verification if required

**Note:** Account activation can take 24-48 hours.

---

## Part 5: Create App in Play Console (1 hour)

### Step 1: Create App

1. Go to https://play.google.com/console
2. Click "Create app"
3. Fill in details:
   - **App name:** Stonk Market Analyzer
   - **Default language:** English (United States)
   - **App or game:** App
   - **Free or paid:** Free
4. Check declarations:
   - [ ] I confirm this app complies with Google Play policies
   - [ ] I confirm this app complies with US export laws
5. Click "Create app"

### Step 2: Set Up App

Complete these sections in the left sidebar:

#### A. App Access
- Select "All functionality is available without restrictions"
- Click "Save"

#### B. Ads
- Select "No, my app does not contain ads"
- Click "Save"

#### C. Content Rating
1. Click "Start questionnaire"
2. Enter email address
3. Select category: "Utility, Productivity, Communication, or Other"
4. Answer questions (all "No" for your app)
5. Click "Submit"
6. Click "Apply rating"

#### D. Target Audience
1. Select age groups: "18 and over"
2. Click "Next"
3. Appeal: "No" (not designed for children)
4. Click "Save"

#### E. News App
- Select "No, it's not a news app"
- Click "Save"

#### F. COVID-19 Contact Tracing
- Select "No"
- Click "Save"

#### G. Data Safety
1. Click "Start"
2. Data collection: "Yes, we collect data"
3. Data types collected:
   - Select "App activity" → "App interactions"
   - Purpose: "Analytics"
   - Data handling: "Data is not shared" and "Data is encrypted in transit"
4. Click "Next" through all sections
5. Click "Submit"

#### H. Government Apps
- Select "No"
- Click "Save"

#### I. Financial Features
- Select "No"
- Click "Save"

### Step 3: Store Listing

Click "Main store listing" in sidebar:

#### App Details

**App name:** Stonk Market Analyzer

**Short description (80 chars):**
```
AI-powered stock analysis with real-time insights and research tools
```

**Full description (4000 chars max):**
```
Stonk Market Analyzer - Your AI-Powered Investment Research Assistant

Make smarter investment decisions with comprehensive stock analysis powered by artificial intelligence.

KEY FEATURES:

📊 Guided Research Flow
• 7-step comprehensive analysis
• Business overview and financials
• Competitive moat assessment
• Risk evaluation
• Valuation analysis
• Investment recommendations

💬 AI Chat Assistant
• Ask any question about stocks
• Get instant, data-driven answers
• Real-time market information

⚖️ Stock Comparison
• Compare up to 3 stocks side-by-side
• See strengths and weaknesses
• Make informed decisions

⭐ Watchlist
• Save your favorite stocks
• Quick access to analysis
• Track your interests

🎯 Real-Time Data
• Latest market information
• Current stock prices
• Recent news and updates

🤖 AI-Powered Insights
• Advanced analysis algorithms
• Comprehensive research
• Professional-grade reports

Whether you're a beginner investor or experienced trader, Stonk Market Analyzer provides the tools and insights you need to research stocks effectively.

DISCLAIMER: This app provides educational information only and is not financial advice. Always consult with a qualified financial advisor before making investment decisions.
```

#### Graphics

**App icon:** (Already set in Android Studio)

**Feature graphic (1024 x 500):**
- Create at https://www.canva.com
- Use template or create custom
- Download and upload

**Phone screenshots (2-8 required):**
1. In Android Studio emulator, take screenshots:
   - Home screen with ticker input
   - Research results page
   - Chat interface
   - Stock comparison
   - Watchlist
2. Save screenshots
3. Upload to Play Console

To take screenshots in emulator:
- Click camera icon in emulator toolbar
- Or use `Cmd+S` (Mac) / `Ctrl+S` (Windows)

**Tablet screenshots:** (Optional but recommended)
- Same as phone but in tablet emulator

#### Categorization

- **App category:** Finance
- **Tags:** stock, market, analysis, investing, AI

#### Contact Details

- **Email:** [Your email]
- **Phone:** [Optional]
- **Website:** https://stonkmarketanalyzer.com
- **Privacy policy URL:** https://stonkmarketanalyzer.com/privacy-policy

(You'll need to create a privacy policy page - see below)

Click "Save"

---

## Part 6: Create Privacy Policy (15 minutes)

Create `frontend/public/privacy-policy.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Privacy Policy - Stonk Market Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        p { line-height: 1.6; }
    </style>
</head>
<body>
    <h1>Privacy Policy for Stonk Market Analyzer</h1>
    <p><strong>Last updated:</strong> November 11, 2025</p>
    
    <h2>Information We Collect</h2>
    <p>We collect anonymous usage analytics to improve the app experience. This includes:</p>
    <ul>
        <li>App interactions and feature usage</li>
        <li>Device type and operating system</li>
        <li>Crash reports and error logs</li>
    </ul>
    <p>We do NOT collect:</p>
    <ul>
        <li>Personal financial information</li>
        <li>Account credentials</li>
        <li>Location data</li>
        <li>Contact information</li>
    </ul>
    
    <h2>How We Use Information</h2>
    <p>We use collected data to:</p>
    <ul>
        <li>Improve app performance and stability</li>
        <li>Understand which features are most useful</li>
        <li>Fix bugs and technical issues</li>
    </ul>
    
    <h2>Data Storage and Security</h2>
    <p>All data is:</p>
    <ul>
        <li>Stored securely on encrypted servers</li>
        <li>Transmitted using HTTPS encryption</li>
        <li>Never sold or shared with third parties</li>
    </ul>
    
    <h2>Third-Party Services</h2>
    <p>We use the following third-party services:</p>
    <ul>
        <li><strong>Perplexity AI:</strong> For stock analysis and research</li>
        <li><strong>Analytics:</strong> For anonymous usage tracking</li>
    </ul>
    
    <h2>Your Rights</h2>
    <p>You have the right to:</p>
    <ul>
        <li>Request deletion of your data</li>
        <li>Opt out of analytics</li>
        <li>Ask questions about data collection</li>
    </ul>
    
    <h2>Children's Privacy</h2>
    <p>This app is not intended for users under 18 years of age.</p>
    
    <h2>Changes to This Policy</h2>
    <p>We may update this privacy policy from time to time. We will notify users of any material changes.</p>
    
    <h2>Contact Us</h2>
    <p>For questions about this privacy policy, contact us at:</p>
    <p>Email: [your-email@example.com]</p>
    <p>Website: https://stonkmarketanalyzer.com</p>
</body>
</html>
```

Deploy this to your website:
```bash
# Copy to frontend public folder
cp privacy-policy.html frontend/public/

# Rebuild and deploy
cd frontend
npm run build
./deployment/deploy-frontend.sh
```

Now your privacy policy is at: https://stonkmarketanalyzer.com/privacy-policy.html

---

## Part 7: Upload and Release (30 minutes)

### Step 1: Create Release

1. In Play Console, go to "Production" in left sidebar
2. Click "Create new release"
3. Click "Upload" and select your `.aab` file
4. Release name: "1.0.0 - Initial Release"
5. Release notes:
```
Initial release of Stonk Market Analyzer!

Features:
• AI-powered stock research
• 7-step guided analysis
• Free chat with AI assistant
• Compare multiple stocks
• Save stocks to watchlist
• Dark mode support

We're excited to help you make better investment decisions!
```
6. Click "Save"
7. Click "Review release"
8. Fix any warnings/errors
9. Click "Start rollout to Production"
10. Confirm rollout

### Step 2: Wait for Review

- **Review time:** 1-7 days (usually 2-3 days)
- **Status:** Check "Publishing overview" in Play Console
- **Notifications:** You'll get email updates

### Step 3: App Goes Live! 🎉

Once approved:
- App appears in Google Play Store
- Users can search and download
- You'll get the Play Store link

---

## Part 8: After Launch

### Monitor Your App

1. **Check reviews:** Respond to user feedback
2. **Monitor crashes:** Fix any issues quickly
3. **Track installs:** See how many downloads
4. **Update regularly:** Add features, fix bugs

### Update Your App

When you make changes:

```bash
# 1. Update code
cd frontend
# Make changes...

# 2. Rebuild
npm run build
npx cap sync android

# 3. Increment version in android/app/build.gradle
versionCode 2  # Increment by 1
versionName "1.0.1"  # Update version

# 4. Build new AAB
# In Android Studio: Build → Generate Signed Bundle

# 5. Upload to Play Console
# Production → Create new release → Upload new AAB
```

---

## Troubleshooting

### "App not installed" error
- Uninstall old version first
- Check if APK is signed correctly

### Build fails
```bash
cd frontend/android
./gradlew clean
./gradlew build
```

### Emulator won't start
- Restart Android Studio
- Check virtualization is enabled in BIOS
- Try creating a new emulator

### App crashes on launch
- Check logs: `View → Tool Windows → Logcat`
- Look for red error messages
- Common issue: API URL not set correctly

---

## Quick Commands Reference

```bash
# Open in Android Studio
cd frontend
npx cap open android

# Build debug APK
cd frontend/android
./gradlew assembleDebug

# Build release AAB
./gradlew bundleRelease

# Sync web changes to Android
cd frontend
npm run build
npx cap sync android

# Check build
./gradlew build --info
```

---

## Checklist Before Submitting

- [ ] App tested in emulator (no crashes)
- [ ] All features work correctly
- [ ] App icon looks good
- [ ] Screenshots taken (2-8 images)
- [ ] Privacy policy created and live
- [ ] Store listing complete
- [ ] Content rating obtained
- [ ] Data safety form filled
- [ ] Release AAB built and signed
- [ ] Release notes written

---

## Timeline

- **Today:** Test app, create assets (2-3 hours)
- **Tomorrow:** Complete store listing, upload AAB (1-2 hours)
- **Day 3-7:** Wait for Google review
- **Day 7:** App goes live! 🚀

---

## Cost Summary

- Google Play Developer: $25 (one-time)
- App icon design: $0 (use free tools)
- **Total:** $25

---

## Support

If you get stuck:
- Android Studio docs: https://developer.android.com/studio/intro
- Capacitor docs: https://capacitorjs.com/docs/android
- Play Console help: https://support.google.com/googleplay/android-developer

---

**You're ready to launch!** Follow these steps and your app will be live on Google Play Store in about a week. Good luck! 🚀
