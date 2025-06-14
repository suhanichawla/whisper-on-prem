#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def create_github_workflow():
    """Create GitHub Actions workflow for automated builds"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)

    workflow_content = """name: Build and Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            asset_name: WhisperSpeechApp-linux-x86_64
          - os: windows-latest
            asset_name: WhisperSpeechApp-windows-AMD64
          - os: macos-latest
            asset_name: WhisperSpeechApp-darwin-arm64

    runs-on: ${{ matrix.os }}

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build executable
      run: python build_executables.py

    - name: Create release archive
      shell: bash
      run: |
        if [ "${{ matrix.os }}" == "windows-latest" ]; then
          7z a ${{ matrix.asset_name }}.zip ./distributions/${{ matrix.asset_name }}/*
        else
          cd distributions && zip -r ${{ matrix.asset_name }}.zip ${{ matrix.asset_name }}
        fi

    - name: Upload Release Asset
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.asset_name }}
        path: distributions/${{ matrix.asset_name }}.zip

  release:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
    - name: Download all artifacts
      uses: actions/download-artifact@v3

    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          */WhisperSpeechApp-*.zip
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

    with open(workflow_dir / "build.yml", "w") as f:
        f.write(workflow_content.strip())

    print("✅ Created GitHub Actions workflow")

def create_simple_server():
    """Create a simple Python server for local testing"""
    server_content = """#!/usr/bin/env python3

import http.server
import socketserver
import os
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "website"), **kwargs)

def main():
    os.chdir(Path(__file__).parent)

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Server running at http://localhost:{PORT}")
        print("📁 Serving files from ./website directory")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n🛑 Server stopped")

if __name__ == "__main__":
    main()
"""

    with open("local_server.py", "w") as f:
        f.write(server_content.strip())

    print("✅ Created local development server")

def create_netlify_config():
    """Create Netlify configuration for easy deployment"""
    netlify_config = """[build]
  command = "echo 'No build needed - static site'"
  publish = "website"

[[headers]]
  for = "/downloads/*"
  [headers.values]
    Content-Type = "application/zip"
    Content-Disposition = "attachment"

[[redirects]]
  from = "/download"
  to = "/"
  status = 301
"""

    with open("netlify.toml", "w") as f:
        f.write(netlify_config.strip())

    print("✅ Created Netlify configuration")

def create_deployment_readme():
    """Create detailed deployment instructions"""
    readme_content = """# Deployment Guide for Whisper Speech App

## Overview

This project includes everything needed to make your app downloadable from a website:

1. **Executable Builder** (`build_executables.py`) - Creates standalone executables
2. **Download Website** (`website/index.html`) - Beautiful download page
3. **Automated Deployment** - GitHub Actions, Netlify, and local testing

## Quick Start

### 1. Build Executables

```bash
# Build for current platform
python build_executables.py

# This creates:
# - dist/ folder with executables
# - distributions/ folder with zip files ready for distribution
```

### 2. Test Locally

```bash
# Start local server
python local_server.py

# Visit http://localhost:8000 to see your download page
```

### 3. Deploy to Web

Choose one of these options:

#### Option A: Netlify (Recommended - Free & Easy)

1. Create account at [netlify.com](https://netlify.com)
2. Connect your GitHub repository
3. Netlify will automatically:
   - Serve your website from the `website/` folder
   - Handle file downloads properly
   - Provide HTTPS and CDN

#### Option B: GitHub Pages

1. Enable GitHub Pages in your repo settings
2. Set source to `website/` folder
3. Your site will be at `https://suhanichawla.github.io/whisper-on-prem`

#### Option C: Any Web Host

1. Upload the `website/` folder to your web host
2. Create a `downloads/` folder
3. Upload your `.zip` files from `distributions/` to `downloads/`

## File Structure

```
whisper-speech-app/
├── main.py                    # Your main application
├── build_executables.py       # Builds standalone executables
├── deploy.py                  # This deployment script
├── local_server.py            # Local testing server
├── website/
│   └── index.html            # Download webpage
├── distributions/            # Generated zip files for download
├── .github/workflows/        # Automated builds (GitHub Actions)
└── netlify.toml             # Netlify configuration
```

## Automated Builds with GitHub Actions

The included GitHub workflow will automatically:

1. Build executables for Windows, macOS, and Linux
2. Create releases when you tag versions
3. Upload distribution files

To use:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# GitHub will automatically build and release
```

## Customization

### Update Download Links

Edit `website/index.html` and update the download URLs if needed:

```html
<a href="downloads/WhisperSpeechApp-darwin-arm64.zip" class="download-btn">
    Download for Mac (Apple Silicon)
</a>
```

### Add Analytics

Add Google Analytics or other tracking to `website/index.html`:

```html
<!-- Add before closing </head> tag -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

### Custom Domain

For custom domains:
- **Netlify**: Add domain in Netlify dashboard
- **GitHub Pages**: Add CNAME file to website folder

## Troubleshooting

### Large File Sizes

Executables might be 100MB+ due to Whisper models. Consider:

1. Using external hosting for large files (AWS S3, Google Drive)
2. Creating installer that downloads models separately
3. Using Git LFS for version control

### Build Issues

```bash
# Clean build
rm -rf dist/ build/ *.spec

# Rebuild
python build_executables.py
```

### Permissions Issues

On macOS/Linux, users might need to:

```bash
# Make executable
chmod +x WhisperSpeechApp

# Or right-click → Open (macOS) to bypass security
```

## Support

For deployment issues:
1. Check GitHub Actions logs for build errors
2. Test locally with `python local_server.py`
3. Verify file paths in HTML match your hosting structure
"""

    with open("DEPLOYMENT.md", "w") as f:
        f.write(readme_content.strip())

    print("✅ Created deployment documentation")

def update_requirements():
    """Add PyInstaller to requirements"""
    requirements_path = Path("requirements.txt")

    if requirements_path.exists():
        with open(requirements_path, "r") as f:
            current_reqs = f.read()

        if "pyinstaller" not in current_reqs.lower():
            with open(requirements_path, "a") as f:
                f.write("\npyinstaller>=5.0\n")
            print("✅ Added PyInstaller to requirements.txt")
    else:
        print("⚠️  requirements.txt not found")

def main():
    print("🚀 Setting up deployment for Whisper Speech App")
    print("=" * 60)

    # Create all deployment files
    create_github_workflow()
    create_simple_server()
    create_netlify_config()
    create_deployment_readme()
    update_requirements()

    # Create necessary directories
    Path("website/downloads").mkdir(parents=True, exist_ok=True)

    print("\n✅ Deployment setup complete!")
    print("\n📋 Next Steps:")
    print("1. Build executables: python build_executables.py")
    print("2. Test locally: python local_server.py")
    print("3. Deploy to web (see DEPLOYMENT.md for options)")
    print("4. Update GitHub repo URL in website/index.html")

    print("\n🌐 Deployment Options:")
    print("• Netlify (recommended): Free, easy, automatic HTTPS")
    print("• GitHub Pages: Free, integrated with GitHub")
    print("• Your own web host: Full control")

    print("\n📖 See DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
