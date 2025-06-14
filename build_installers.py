#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def safe_print(message):
    """Print message with fallback for Windows encoding issues"""
    try:
        print(message)
    except UnicodeEncodeError:
        ascii_message = message.replace("🚀", "[*]").replace("✅", "[OK]").replace("📦", "[PKG]").replace("❌", "[ERR]").replace("⚠️", "[WARN]").replace("🏗️", "[BUILD]").replace("📁", "[DIR]")
        print(ascii_message.encode('ascii', errors='ignore').decode('ascii'))

def run_command(cmd, description="", cwd=None):
    """Run a command and handle errors"""
    if description:
        safe_print(f"🏗️ {description}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Error: {e}")
        safe_print(f"❌ Output: {e.stdout}")
        safe_print(f"❌ Error: {e.stderr}")
        return False, str(e)

def create_license_file():
    """Create a license file for installers"""
    license_content = """MIT License

Copyright (c) 2024 Suhani Chawla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    # Ensure directory exists
    os.makedirs("installers/windows", exist_ok=True)

    with open("installers/windows/license.txt", "w") as f:
        f.write(license_content)

    safe_print("✅ Created license file")

def build_windows_installer():
    """Build Windows NSIS installer"""
    safe_print("🏗️ Building Windows installer...")

    # Check if dist directory exists
    if not os.path.exists("dist/WhisperSpeechApp"):
        safe_print("❌ dist/WhisperSpeechApp directory not found. Please build executables first.")
        return False

    # Check if NSIS is available
    nsis_paths = [
        "C:\\Program Files (x86)\\NSIS\\makensis.exe",
        "C:\\Program Files\\NSIS\\makensis.exe",
        "makensis.exe"  # If in PATH
    ]

    nsis_exe = None
    for path in nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_exe = path
            break

    if not nsis_exe:
        safe_print("⚠️  NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
        safe_print("   Download and install, then rerun this script.")
        return False

    # Ensure directories exist
    os.makedirs("installers/windows", exist_ok=True)
    os.makedirs("distributions", exist_ok=True)

    # Create license file
    create_license_file()

    # Change to the installers/windows directory to run NSIS
    original_dir = os.getcwd()
    try:
        os.chdir("installers/windows")

        # Build installer (NSIS will create the .exe in the current directory)
        cmd = f'"{nsis_exe}" installer.nsi'
        success, output = run_command(cmd, "Creating Windows installer")

        if success:
            # Check if installer was created
            if os.path.exists("WhisperSpeechApp-Setup.exe"):
                # Move installer to distributions folder
                shutil.move("WhisperSpeechApp-Setup.exe", "../../distributions/")
                safe_print("✅ Windows installer created: distributions/WhisperSpeechApp-Setup.exe")
                return True
            else:
                safe_print("❌ Installer was not created")
                return False
        else:
            return False

    finally:
        # Always return to original directory
        os.chdir(original_dir)

def build_macos_installer():
    """Build macOS DMG installer"""
    safe_print("🏗️ Building macOS installer...")

    # Ensure script exists and is executable
    script_path = "installers/macos/create_dmg.sh"
    if not os.path.exists(script_path):
        safe_print(f"❌ Script not found: {script_path}")
        return False

    # Make script executable
    os.chmod(script_path, 0o755)

    # Run DMG creation script
    success, output = run_command(f"bash {script_path}", "Creating macOS DMG")

    if success:
        safe_print("✅ macOS installer created")
        return True

    return False

def build_linux_installer():
    """Build Linux AppImage and .deb package"""
    safe_print("🏗️ Building Linux installers...")

    # Ensure script exists and is executable
    script_path = "installers/linux/create_appimage.sh"
    if not os.path.exists(script_path):
        safe_print(f"❌ Script not found: {script_path}")
        return False

    # Make script executable
    os.chmod(script_path, 0o755)

    # Run AppImage creation script
    success, output = run_command(f"bash {script_path}", "Creating Linux packages")

    if success:
        safe_print("✅ Linux installers created")
        return True

    return False

def main():
    safe_print("🚀 Building Professional Installers for Whisper Speech App")
    safe_print("=" * 60)

    # First, build the executables
    safe_print("📦 Step 1: Building executables...")
    success, _ = run_command("python build_executables.py", "Building executables")

    if not success:
        safe_print("❌ Failed to build executables. Please fix errors and try again.")
        sys.exit(1)

    # Create installers directory
    os.makedirs("distributions", exist_ok=True)

    current_platform = platform.system().lower()
    safe_print(f"🖥️ Current platform: {current_platform}")

    success_count = 0
    total_count = 0

    # Build platform-specific installer
    if current_platform == "windows":
        total_count += 1
        if build_windows_installer():
            success_count += 1

    elif current_platform == "darwin":
        total_count += 1
        if build_macos_installer():
            success_count += 1

    elif current_platform == "linux":
        total_count += 1
        if build_linux_installer():
            success_count += 1

    else:
        safe_print(f"⚠️  Platform {current_platform} not supported for installer creation")

    # Summary
    safe_print("\n" + "=" * 60)
    if success_count == total_count and total_count > 0:
        safe_print("✅ All installers built successfully!")
        safe_print("\n📋 Created installers:")

        # List created files
        if os.path.exists("distributions"):
            for file in os.listdir("distributions"):
                if file.endswith(('.exe', '.dmg', '.AppImage', '.deb')):
                    safe_print(f"   📦 {file}")

        safe_print("\n🎉 Your app now has professional installers!")
        safe_print("Users can double-click to install - no technical knowledge required!")

    else:
        safe_print("❌ Some installers failed to build. Check the errors above.")

    safe_print("\n📖 Next steps:")
    safe_print("1. Test the installer on a clean system")
    safe_print("2. Upload to GitHub releases")
    safe_print("3. Update your website download links")

if __name__ == "__main__":
    main()
