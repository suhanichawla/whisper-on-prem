#!/bin/bash

# Linux AppImage Creator for Whisper Speech App
# Creates a portable AppImage that works on any Linux distribution

APP_NAME="Whisper Speech App"
APP_VERSION="1.0.0"
APP_ID="com.suhanichawla.whisperspeechapp"
APPIMAGE_NAME="WhisperSpeechApp-${APP_VERSION}-x86_64.AppImage"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Linux AppImage for ${APP_NAME}${NC}"

# Check if built app exists
if [ ! -d "dist/WhisperSpeechApp" ]; then
    echo -e "${RED}Error: Built app not found at dist/WhisperSpeechApp${NC}"
    echo "Please build the app first using: python build_executables.py"
    exit 1
fi

# Create AppDir structure
APPDIR="WhisperSpeechApp.AppDir"
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${APPDIR}/usr/share/metainfo"

echo -e "${YELLOW}Copying application files...${NC}"
cp -r dist/WhisperSpeechApp/* "${APPDIR}/usr/bin/"

# Make the main executable
chmod +x "${APPDIR}/usr/bin/WhisperSpeechApp"

# Create desktop file
cat > "${APPDIR}/usr/share/applications/${APP_ID}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=Privacy-focused speech-to-text using OpenAI Whisper
Exec=WhisperSpeechApp
Icon=${APP_ID}
Categories=AudioVideo;Audio;Utility;
Keywords=speech;text;transcription;whisper;voice;
StartupNotify=true
NoDisplay=false
EOF

# Create AppRun executable
cat > "${APPDIR}/AppRun" << 'EOF'
#!/bin/bash

# AppRun script for Whisper Speech App
APPDIR="$(dirname "$(readlink -f "${0}")")"

# Set up environment
export PATH="${APPDIR}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"

# Change to the app directory
cd "${APPDIR}/usr/bin"

# Run the application
exec "${APPDIR}/usr/bin/WhisperSpeechApp" "$@"
EOF

chmod +x "${APPDIR}/AppRun"

# Create desktop file in root
cp "${APPDIR}/usr/share/applications/${APP_ID}.desktop" "${APPDIR}/"

# Create icon (you can replace this with your actual icon)
cat > "${APPDIR}/${APP_ID}.png" << 'EOF'
# This is a placeholder for the app icon
# In a real deployment, you would copy your actual PNG icon here
# For now, we'll create a simple text-based icon
EOF

# Copy icon to proper location
cp "${APPDIR}/${APP_ID}.png" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/"

# Create AppStream metainfo
cat > "${APPDIR}/usr/share/metainfo/${APP_ID}.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>${APP_ID}</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>${APP_NAME}</name>
  <summary>Privacy-focused speech-to-text using OpenAI Whisper</summary>
  <description>
    <p>
      A desktop application that converts speech to text using OpenAI's Whisper models
      running locally on your machine. Perfect for companies that don't allow cloud-based
      speech recognition tools.
    </p>
    <p>Features:</p>
    <ul>
      <li>100% private - all processing happens locally</li>
      <li>Multiple Whisper models (tiny to large)</li>
      <li>Global hotkey support</li>
      <li>Auto-paste transcribed text</li>
    </ul>
  </description>
  <launchable type="desktop-id">${APP_ID}.desktop</launchable>
  <url type="homepage">https://github.com/suhanichawla/whisper-on-prem</url>
  <url type="bugtracker">https://github.com/suhanichawla/whisper-on-prem/issues</url>
  <screenshots>
    <screenshot type="default">
      <caption>Main application window</caption>
    </screenshot>
  </screenshots>
  <releases>
    <release version="${APP_VERSION}" date="$(date +%Y-%m-%d)"/>
  </releases>
</component>
EOF

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo -e "${YELLOW}Downloading appimagetool...${NC}"
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create the AppImage
echo -e "${YELLOW}Creating AppImage...${NC}"
./appimagetool-x86_64.AppImage "${APPDIR}" "${APPIMAGE_NAME}"

# Move to distributions folder
mkdir -p distributions
mv "${APPIMAGE_NAME}" distributions/

# Create .deb package as well
echo -e "${YELLOW}Creating .deb package...${NC}"
DEB_DIR="whisper-speech-app_${APP_VERSION}_amd64"
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps"

# Copy files for .deb
cp -r dist/WhisperSpeechApp/* "${DEB_DIR}/usr/bin/"
cp "${APPDIR}/usr/share/applications/${APP_ID}.desktop" "${DEB_DIR}/usr/share/applications/"
cp "${APPDIR}/${APP_ID}.png" "${DEB_DIR}/usr/share/icons/hicolor/256x256/apps/"

# Create control file
cat > "${DEB_DIR}/DEBIAN/control" << EOF
Package: whisper-speech-app
Version: ${APP_VERSION}
Section: sound
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6, portaudio19-dev
Maintainer: Suhani Chawla <suhani@example.com>
Description: Privacy-focused speech-to-text application
 A desktop application that converts speech to text using OpenAI's Whisper
 models running locally on your machine. Perfect for companies that don't
 allow cloud-based speech recognition tools.
Homepage: https://github.com/suhanichawla/whisper-on-prem
EOF

# Create postinst script
cat > "${DEB_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/bash
# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor
fi
EOF

chmod +x "${DEB_DIR}/DEBIAN/postinst"

# Build .deb package
dpkg-deb --build "${DEB_DIR}"
mv "${DEB_DIR}.deb" distributions/

# Clean up
rm -rf "${APPDIR}"
rm -rf "${DEB_DIR}"

echo -e "${GREEN}✅ Linux packages created successfully:${NC}"
echo -e "  🐧 distributions/${APPIMAGE_NAME} (portable AppImage)"
echo -e "  📦 distributions/whisper-speech-app_${APP_VERSION}_amd64.deb (Debian/Ubuntu package)"
echo -e "${GREEN}Users can now double-click the AppImage or install the .deb package!${NC}"
