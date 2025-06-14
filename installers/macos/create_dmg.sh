#!/bin/bash

# macOS DMG Creator for Whisper Speech App
# Creates a professional .dmg file with drag-and-drop installation

APP_NAME="Whisper Speech App"
APP_VERSION="1.0.0"
DMG_NAME="WhisperSpeechApp-${APP_VERSION}"
APP_BUNDLE="WhisperSpeechApp.app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating macOS DMG installer for ${APP_NAME}${NC}"

# Check if app bundle exists
if [ ! -d "dist/${APP_BUNDLE}" ]; then
    echo -e "${RED}Error: App bundle not found at dist/${APP_BUNDLE}${NC}"
    echo "Please build the app first using: python build_executables.py"
    exit 1
fi

# Create temporary DMG directory
TEMP_DIR="temp_dmg"
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}"

echo -e "${YELLOW}Copying app bundle...${NC}"
cp -R "dist/${APP_BUNDLE}" "${TEMP_DIR}/"

# Create Applications symlink for drag-and-drop
echo -e "${YELLOW}Creating Applications symlink...${NC}"
ln -sf /Applications "${TEMP_DIR}/Applications"

# Add README and license
cat > "${TEMP_DIR}/README.txt" << EOF
# Whisper Speech App - macOS Installation

## Quick Installation
1. Drag "Whisper Speech App.app" to the Applications folder
2. Launch from Applications or Spotlight search

## First Run
- The app will request microphone permissions
- Whisper models will download automatically (may take a few minutes)

## Usage
- Hold Fn key (or Cmd+Space) while speaking to record
- Text will be transcribed and pasted automatically
- App runs in system tray/menu bar

## System Requirements
- macOS 10.14 or later
- Microphone access
- Internet connection for initial model download

## Support
Visit: https://github.com/suhanichawla/whisper-on-prem

© 2024 Suhani Chawla. All rights reserved.
EOF

# Create custom DMG background (if you have one)
if [ -f "installers/macos/dmg_background.png" ]; then
    cp "installers/macos/dmg_background.png" "${TEMP_DIR}/.background.png"
fi

# Calculate size needed
echo -e "${YELLOW}Calculating DMG size...${NC}"
SIZE=$(du -sm "${TEMP_DIR}" | awk '{print $1}')
SIZE=$((SIZE + 50)) # Add 50MB padding

echo -e "${YELLOW}Creating temporary DMG (${SIZE}MB)...${NC}"
# Create temporary DMG
hdiutil create -srcfolder "${TEMP_DIR}" -volname "${APP_NAME}" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${SIZE}m "temp_${DMG_NAME}.dmg"

# Mount the temporary DMG
echo -e "${YELLOW}Mounting DMG for customization...${NC}"
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "temp_${DMG_NAME}.dmg" | \
    egrep '^/dev/' | sed 1q | awk '{print $1}')

# Customize the DMG appearance
echo -e "${YELLOW}Customizing DMG appearance...${NC}"
osascript << EOF
tell application "Finder"
    tell disk "${APP_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 920, 420}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set background picture of viewOptions to file ".background.png"

        -- Position items
        set position of item "${APP_BUNDLE}" of container window to {130, 150}
        set position of item "Applications" of container window to {390, 150}
        set position of item "README.txt" of container window to {260, 280}

        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

# Sync and unmount
sync
hdiutil detach "${DEVICE}"

# Convert to final compressed DMG
echo -e "${YELLOW}Creating final compressed DMG...${NC}"
hdiutil convert "temp_${DMG_NAME}.dmg" -format UDZO -imagekey zlib-level=9 -o "${DMG_NAME}.dmg"

# Clean up
rm -f "temp_${DMG_NAME}.dmg"
rm -rf "${TEMP_DIR}"

# Move to distributions folder
mkdir -p distributions
mv "${DMG_NAME}.dmg" distributions/

echo -e "${GREEN}✅ DMG created successfully: distributions/${DMG_NAME}.dmg${NC}"
echo -e "${GREEN}Users can now double-click to mount and drag the app to Applications!${NC}"

# Optional: Create a ZIP for backwards compatibility
echo -e "${YELLOW}Creating ZIP backup...${NC}"
cd dist && zip -r "../distributions/WhisperSpeechApp-darwin-$(uname -m).zip" "${APP_BUNDLE}"
cd ..

echo -e "${GREEN}✅ Installation packages created:${NC}"
echo -e "  📀 distributions/${DMG_NAME}.dmg (recommended)"
echo -e "  📦 distributions/WhisperSpeechApp-darwin-$(uname -m).zip (backup)"
