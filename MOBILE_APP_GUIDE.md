# Mobile App Deployment Guide - Stonk Market Analyzer

Your web app has been converted to mobile! Follow these steps to publish.

## ✅ What's Done

- ✅ Capacitor installed and configured
- ✅ Android project created (`frontend/android/`)
- ✅ iOS project created (`frontend/ios/`)
- ✅ Web assets built and copied
- ✅ App ID: `com.adityakathera.stonkanalyzer`
- ✅ App Name: "Stonk Market Analyzer"

## 📱 Current Status

- **Android**: Ready to build ✅
- **iOS**: Needs Xcode (Mac only) ⚠️
- **Backend**: No changes needed ✅

---

## Part 1: Account Setup (Do This First)

### A. Google Play Developer Account (For Android)

1. Go to https://play.google.com/console/signup
2. Sign in with your Google account
3. Pay $25 one-time registration fee
4. Accept Developer Distribution Agreement
5. Complete account details
6. **Time:** 15-30 minutes
7. **Note:** Account activation can take 24-48 hours

### B. Apple Developer Account (For iOS)

1. Go to https://developer.apple.com/programs/enroll/
2. Sign in with your Apple ID
3. Pay $99/year enrollment fee
4. Complete enrollment (may require D-U-N-S number for companies)
5. **Time:** 15-30 minutes
6. **Note:** Approval can take 24-48 hours

---

## Part 2: Android App Build & Deployment

### Prerequisites

- ✅ Android Studio installed (download from https://developer.android.com/studio)
- ✅ Java JDK 11+ installed
- ✅ Google Play Developer account active

### Step 1: Open Android Project

```bash
cd frontend
npx cap open android
```

This opens Android Studio with your project.

### Step 2: Configure App Details

In Android Studio:

1. Open `android/app/src/main/res/values/strings.xml`
2. Verify app name is correct
3. Open `android/app/build.gradle`
4. Update version:
   ```gradle
   versionCode 1
   versionName "1.0.0"
   ```

### Step 3: Generate Signing Key

```bash
# In your project root
keytool -genkey -v -keystore stonk-release-key.keystore -alias stonk-key -keyalg RSA -keysize 2048 -validity 10000

# Answer the prompts:
# - Password: [choose a strong password]
# - Name: Aditya Kathera
# - Organization: [your company or leave blank]
# - City, State, Country: [your location]
```

**IMPORTANT:** Save this keystore file and password securely! You'll need it for all future updates.

### Step 4: Configure Signing in Android Studio

1. In Android Studio, go to `Build` → `Generate Signed Bundle / APK`
2. Select `Android App Bundle`
3. Click `Next`
4. Choose your keystore file
5. Enter passwords
6. Select `release` build variant
7. Click `Finish`

### Step 5: Test the APK

```bash
# Build debug version first to test
cd frontend/android
./gradlew assembleDebug

# Install on connected device or emulator
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Step 6: Upload to Google Play Console

1. Go to https://play.google.com/console
2. Click "Create app"
3. Fill in app details:
   - **App name:** Stonk Market Analyzer
   - **Default language:** English (US)
   - **App or game:** App
   - **Free or paid:** Free
4. Complete the questionnaire
5. Go to "Production" → "Create new release"
6. Upload your `.aab` file from `android/app/build/outputs/bundle/release/`
7. Fill in release notes
8. Complete store listing:
   - **Short description:** AI-powered stock market analysis tool
   - **Full description:** [Write detailed description]
   - **Screenshots:** Take 2-8 screenshots (use Android emulator)
   - **App icon:** 512x512 PNG
   - **Feature graphic:** 1024x500 PNG
9. Set content rating (complete questionnaire)
10. Select target audience
11. Submit for review

**Review time:** 1-7 days typically

---

## Part 3: iOS App Build & Deployment

### Prerequisites

- ✅ Mac computer with macOS
- ✅ Xcode installed (from Mac App Store)
- ✅ Apple Developer account active
- ✅ CocoaPods installed: `sudo gem install cocoapods`

### Step 1: Install iOS Dependencies

```bash
cd frontend/ios/App
pod install
```

### Step 2: Open iOS Project

```bash
cd frontend
npx cap open ios
```

This opens Xcode with your project.

### Step 3: Configure in Xcode

1. Select your project in the navigator
2. Under "Signing & Capabilities":
   - Select your Team (Apple Developer account)
   - Bundle Identifier: `com.adityakathera.stonkanalyzer`
3. Update version and build number:
   - Version: 1.0.0
   - Build: 1

### Step 4: Add App Icons

1. Create app icons (1024x1024 PNG)
2. Use https://appicon.co to generate all sizes
3. Drag icons into `Assets.xcassets/AppIcon.appiconset/`

### Step 5: Build and Archive

1. In Xcode, select "Any iOS Device" as target
2. Go to `Product` → `Archive`
3. Wait for build to complete
4. Click "Distribute App"
5. Select "App Store Connect"
6. Follow the wizard

### Step 6: Upload to App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" → "+" → "New App"
3. Fill in app information:
   - **Platform:** iOS
   - **Name:** Stonk Market Analyzer
   - **Primary Language:** English (US)
   - **Bundle ID:** com.adityakathera.stonkanalyzer
   - **SKU:** stonkanalyzer001
4. Complete app information:
   - **Category:** Finance
   - **Screenshots:** 6.5" and 5.5" display sizes
   - **Description:** [Write detailed description]
   - **Keywords:** stock, market, analysis, AI, investing
   - **Support URL:** https://stonkmarketanalyzer.com
   - **Privacy Policy URL:** [Create one]
5. Submit for review

**Review time:** 1-3 days typically

---

## Part 4: App Store Assets Needed

### Screenshots (Required)

**Android:**
- Phone: 1080x1920 (minimum 2 screenshots)
- Tablet: 1920x1080 (optional)

**iOS:**
- 6.5" Display: 1284x2778
- 5.5" Display: 1242x2208

**How to capture:**
1. Run app in emulator/simulator
2. Use different screens (home, research, chat, comparison)
3. Take screenshots of key features

### App Icon (Required)

- **Size:** 1024x1024 PNG
- **No transparency**
- **No rounded corners** (system adds them)

**Design tips:**
- Use your rocket 🚀 and chart 📊 emoji
- Simple, recognizable design
- Looks good at small sizes

### Feature Graphic (Android Only)

- **Size:** 1024x500 PNG
- Promotional banner for Play Store

### Descriptions

**Short (80 chars):**
```
AI-powered stock analysis with real-time insights and research tools
```

**Long (4000 chars max):**
```
Stonk Market Analyzer - Your AI-Powered Investment Research Assistant

Make smarter investment decisions with comprehensive stock analysis powered by artificial intelligence.

KEY FEATURES:

📊 Guided Research Flow
- 7-step comprehensive analysis
- Business overview and financials
- Competitive moat assessment
- Risk evaluation
- Valuation analysis
- Investment recommendations

💬 AI Chat Assistant
- Ask any question about stocks
- Get instant, data-driven answers
- Real-time market information

⚖️ Stock Comparison
- Compare up to 3 stocks side-by-side
- See strengths and weaknesses
- Make informed decisions

⭐ Watchlist
- Save your favorite stocks
- Quick access to analysis
- Track your interests

🎯 Real-Time Data
- Latest market information
- Current stock prices
- Recent news and updates

🤖 AI-Powered Insights
- Advanced analysis algorithms
- Comprehensive research
- Professional-grade reports

Whether you're a beginner investor or experienced trader, Stonk Market Analyzer provides the tools and insights you need to research stocks effectively.

DISCLAIMER: This app provides educational information only and is not financial advice. Always consult with a qualified financial advisor before making investment decisions.
```

---

## Part 5: Privacy Policy (Required)

You need a privacy policy URL. Create a simple one:

```markdown
# Privacy Policy for Stonk Market Analyzer

Last updated: [Date]

## Information We Collect
- Anonymous usage analytics
- No personal financial information
- No account creation required

## How We Use Information
- Improve app performance
- Understand feature usage
- Fix bugs and issues

## Data Storage
- Analytics stored securely
- No personal data sold or shared
- Data encrypted in transit

## Third-Party Services
- Perplexity AI for stock analysis
- Standard analytics tools

## Contact
For questions: [your email]

## Changes
We may update this policy. Check this page for updates.
```

Host this at: `https://stonkmarketanalyzer.com/privacy-policy`

---

## Part 6: Testing Before Release

### Android Testing

```bash
# Build and install debug version
cd frontend
npm run build
npx cap sync android
npx cap open android

# In Android Studio:
# 1. Click "Run" (green play button)
# 2. Select device/emulator
# 3. Test all features
```

### iOS Testing (on Mac)

```bash
# Build and run
cd frontend
npm run build
npx cap sync ios
npx cap open ios

# In Xcode:
# 1. Select simulator
# 2. Click "Run" (play button)
# 3. Test all features
```

### Test Checklist

- [ ] App launches successfully
- [ ] All screens load correctly
- [ ] Stock research works
- [ ] Chat interface works
- [ ] Stock comparison works
- [ ] Watchlist saves/loads
- [ ] Dark mode toggles
- [ ] No crashes or errors
- [ ] API calls work (internet required)
- [ ] Responsive on different screen sizes

---

## Part 7: Updating the App

When you make changes:

```bash
# 1. Update web code
cd frontend
# Make your changes...

# 2. Rebuild
npm run build

# 3. Sync to mobile
npx cap sync

# 4. Increment version numbers
# Android: android/app/build.gradle (versionCode and versionName)
# iOS: Xcode project settings (Version and Build)

# 5. Build and upload new version
# Follow same steps as initial release
```

---

## Part 8: Troubleshooting

### Android Build Errors

**"SDK not found":**
```bash
# Set ANDROID_HOME environment variable
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

**"Gradle build failed":**
```bash
cd frontend/android
./gradlew clean
./gradlew build
```

### iOS Build Errors

**"CocoaPods not installed":**
```bash
sudo gem install cocoapods
cd frontend/ios/App
pod install
```

**"Signing error":**
- Check Apple Developer account is active
- Verify Bundle ID matches
- Ensure certificates are valid

### App Crashes

**Check logs:**
```bash
# Android
adb logcat | grep Capacitor

# iOS (in Xcode)
# Window → Devices and Simulators → View Device Logs
```

---

## Part 9: Cost Summary

### One-Time Costs
- Google Play Developer: $25
- App icon design (optional): $0-50 (use Canva free)

### Annual Costs
- Apple Developer: $99/year
- Domain (already have): $12/year
- EC2 hosting (already have): ~$10-20/month

### Total to Launch
- **Android only:** $25
- **iOS only:** $99
- **Both platforms:** $124

---

## Part 10: Timeline

### If you start now:

**Day 1 (Today):**
- ✅ Mobile project created
- ⏳ Register developer accounts (15-30 min)
- ⏳ Create app icons and screenshots (1-2 hours)
- ⏳ Write descriptions and privacy policy (30 min)
- ⏳ Build and test Android APK (1 hour)

**Day 2-3:**
- ⏳ Wait for developer account approval (24-48 hours)

**Day 4:**
- ⏳ Upload to Google Play Console (1 hour)
- ⏳ Submit for review

**Day 5-11:**
- ⏳ Wait for Google Play review (1-7 days)
- ⏳ **Android app goes live!** 🎉

**iOS:** Add 1-3 days for review after upload

---

## Quick Start Commands

```bash
# Build web app
cd frontend
npm run build

# Sync to mobile platforms
npx cap sync

# Open in Android Studio
npx cap open android

# Open in Xcode (Mac only)
npx cap open ios

# Run on device
npx cap run android
npx cap run ios
```

---

## Support & Resources

- **Capacitor Docs:** https://capacitorjs.com/docs
- **Android Studio:** https://developer.android.com/studio
- **Xcode:** https://developer.apple.com/xcode/
- **Google Play Console:** https://play.google.com/console
- **App Store Connect:** https://appstoreconnect.apple.com

---

## Next Steps

1. **Register accounts** (Google Play + Apple Developer)
2. **Create app assets** (icons, screenshots, descriptions)
3. **Test the app** (Android Studio emulator)
4. **Build release version** (signed APK/AAB)
5. **Upload to stores** (Google Play + App Store)
6. **Wait for approval** (1-7 days)
7. **Launch!** 🚀

---

**Your app is ready to go mobile!** The backend requires no changes - it will work exactly as is. The mobile apps will call the same API at `https://api.stonkmarketanalyzer.com`.

Good luck with your launch! 🎉
