# 🚀 GitHub Pages & Release Setup Guide

This guide will help you set up your Whisper Speech App for download from a professional website hosted on GitHub Pages, with automated builds and releases.

## 📋 What You'll Get

- ✨ **Professional download website** at `https://yourusername.github.io/whisper-speech-app`
- 🤖 **Automated builds** for Windows, macOS (Intel & Apple Silicon), and Linux
- 📦 **Automatic releases** when you create version tags
- 🔗 **Dynamic download links** that always point to the latest release
- 📱 **Mobile-responsive design** that works on all devices

## 🎯 Step-by-Step Instructions

### Step 1: Push to GitHub

1. **Create a new repository** on GitHub named `whisper-speech-app` (or your preferred name)

2. **Push your code** to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit with download website setup"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/whisper-speech-app.git
   git push -u origin main
   ```

### Step 2: Configure GitHub Pages

1. **Go to your repository** on GitHub
2. **Click Settings** tab
3. **Scroll to "Pages"** in the left sidebar
4. **Set Source** to "GitHub Actions"
5. **Save** the settings

### Step 3: Update Website Configuration

1. **Edit `website/index.html`** and update these lines (around line 245):
   ```javascript
   const GITHUB_OWNER = 'YOUR_ACTUAL_USERNAME'; // Replace with your GitHub username
   const GITHUB_REPO = 'whisper-speech-app'; // Replace with your actual repo name
   ```

2. **Edit `website/_config.yml`** and update:
   ```yaml
   url: "https://YOUR_ACTUAL_USERNAME.github.io"
   baseurl: "/whisper-speech-app"  # or your actual repo name
   author: "YOUR_ACTUAL_NAME"
   ```

### Step 4: Create Your First Release

1. **Build locally first** (optional, to test):
   ```bash
   python build_executables.py
   ```

2. **Create and push a version tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Watch the magic happen**:
   - Go to your repo's "Actions" tab
   - You'll see two workflows running:
     - "Build and Release" - creates executables
     - "Deploy to GitHub Pages" - updates your website

### Step 5: Wait and Test

1. **Wait for workflows to complete** (5-10 minutes)
2. **Check your releases**: `https://github.com/YOUR_USERNAME/whisper-speech-app/releases`
3. **Visit your website**: `https://YOUR_USERNAME.github.io/whisper-speech-app`
4. **Test download links** - they should work automatically!

## 🔧 Configuration Details

### Repository Settings Required

Make sure these are enabled in your GitHub repo settings:

- **Settings → Actions → General**:
  - ✅ Allow all actions and reusable workflows
  - ✅ Read and write permissions for GITHUB_TOKEN

- **Settings → Pages**:
  - ✅ Source: GitHub Actions

### File Structure

Your repository should look like this:
```
whisper-speech-app/
├── .github/workflows/
│   ├── build.yml           # Builds executables and creates releases
│   └── deploy-pages.yml    # Deploys website to GitHub Pages
├── website/
│   ├── index.html          # Your download website
│   └── _config.yml         # Jekyll configuration
├── main.py                 # Your main application
├── build_executables.py    # Build script
└── requirements.txt        # Python dependencies
```

## 🎉 How It Works

### Automatic Builds
When you push a tag like `v1.0.0`:
1. GitHub Actions builds executables for 4 platforms:
   - Windows (AMD64)
   - macOS Apple Silicon (ARM64)
   - macOS Intel (x86_64)
   - Linux (x86_64)
2. Creates a GitHub release with all zip files
3. Updates your website automatically

### Dynamic Download Links
Your website:
1. Fetches the latest release info from GitHub API
2. Updates version number and release date
3. Links download buttons directly to release assets
4. Shows fallback links if API fails

### Professional Website
Your users will see:
- Auto-detection of their operating system
- Clean, modern design with animations
- Clear installation instructions
- System requirements
- Version information

## 🐛 Troubleshooting

### Build Fails
- Check the "Actions" tab for error details
- Most common issue: missing dependencies in `requirements.txt`
- Make sure PyInstaller installs correctly

### Website Not Updating
- Check that GitHub Pages is set to "GitHub Actions" mode
- Verify the `deploy-pages.yml` workflow completed successfully
- Changes can take a few minutes to appear

### Download Links Not Working
- Verify `GITHUB_OWNER` and `GITHUB_REPO` are correct in `index.html`
- Check that releases exist at: `https://github.com/YOUR_USERNAME/whisper-speech-app/releases`
- Test the GitHub API URL manually: `https://api.github.com/repos/YOUR_USERNAME/whisper-speech-app/releases/latest`

## 🚀 Making Updates

### For Code Changes
```bash
git add .
git commit -m "Update app functionality"
git push origin main
```

### For New Releases
```bash
git tag v1.1.0
git push origin v1.1.0
```

The website and downloads will update automatically!

## 📞 Next Steps

1. **Customize the website** - edit colors, text, add your branding
2. **Add analytics** - Google Analytics, Plausible, etc.
3. **Custom domain** - point your own domain to GitHub Pages
4. **Add more platforms** - maybe ARM Linux, older macOS versions

Your professional download site will be live at:
**`https://YOUR_USERNAME.github.io/whisper-speech-app`**

Happy deploying! 🎉
