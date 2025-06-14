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
        # Replace common emojis with ASCII alternatives
        ascii_message = message.replace("🚀", "[*]").replace("✅", "[OK]").replace("📦", "[PKG]").replace("❌", "[ERR]").replace("⚠️", "[WARN]").replace("🏗️", "[BUILD]").replace("📁", "[DIR]")
        print(ascii_message.encode('ascii', errors='ignore').decode('ascii'))

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        safe_print("✅ PyInstaller already installed")
    except ImportError:
        safe_print("📦 Installing PyInstaller...")
        try:
            # Try installing from public PyPI (workaround for corporate environments)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--index-url", "https://pypi.org/simple/",
                "--trusted-host", "pypi.org",
                "pyinstaller"
            ])
        except subprocess.CalledProcessError:
            safe_print("⚠️  Failed to install from public PyPI, trying alternative...")
            try:
                # Alternative: try with --user flag
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user",
                    "--index-url", "https://pypi.org/simple/",
                    "--trusted-host", "pypi.org",
                    "pyinstaller"
                ])
            except subprocess.CalledProcessError as e:
                safe_print(f"❌ Failed to install PyInstaller: {e}")
                safe_print("\n🔧 Manual installation required:")
                safe_print("Try running one of these commands:")
                safe_print("  pip install --index-url https://pypi.org/simple/ pyinstaller")
                safe_print("  pip install --user --index-url https://pypi.org/simple/ pyinstaller")
                safe_print("  python -m pip install --upgrade --index-url https://pypi.org/simple/ pyinstaller")
                sys.exit(1)

def create_spec_file():
    """Create PyInstaller spec file with proper configuration"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect whisper model files and other data
try:
    whisper_datas = collect_data_files('whisper')
except Exception:
    whisper_datas = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=whisper_datas,
    hiddenimports=[
        'whisper',
        'numpy',
        'pyaudio',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'pynput',
        'pyperclip',
        'ssl',
        'certifi',
        'wave',
        'tempfile',
        'threading',
        'queue',
        'gc',
        'atexit',
        'signal',
        'subprocess'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'torchaudio',
        'tensorflow',
        'matplotlib',
        'scipy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhisperSpeechApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperSpeechApp',
)

# For macOS, create app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='WhisperSpeechApp.app',
        icon='icon.icns' if os.path.exists('icon.icns') else None,
        bundle_identifier='com.yourname.whisperspeechapp',
        info_plist={
            'CFBundleDisplayName': 'Whisper Speech App',
            'CFBundleVersion': '1.0.0',
            'LSUIElement': True,  # Hide from dock (background app)
            'NSMicrophoneUsageDescription': 'This app needs microphone access for speech recognition.',
        }
    )
'''

    with open('whisper_app.spec', 'w') as f:
        f.write(spec_content.strip())
    safe_print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    safe_print(f"🏗️ Building executable for {system}...")

    try:
        # Clean previous builds
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('build'):
            shutil.rmtree('build')

        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "whisper_app.spec", "--clean"]
        subprocess.check_call(cmd)

        safe_print("✅ Executable built successfully!")
        safe_print(f"📁 Output location: {os.path.abspath('dist')}")

        # Create distribution folder
        create_distribution_package(system)

    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Build failed: {e}")
        return False

    return True

def create_distribution_package(system):
    """Create a complete distribution package"""
    dist_name = f"WhisperSpeechApp-{system}-{platform.machine()}"
    dist_dir = Path(f"distributions/{dist_name}")

    # Remove existing distribution directory if it exists
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Create distribution directory
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Copy built application
    if system == "darwin":
        app_source = Path("dist/WhisperSpeechApp.app")
        if app_source.exists():
            shutil.copytree(app_source, dist_dir / "WhisperSpeechApp.app")
        else:
            safe_print(f"⚠️  macOS app bundle not found at {app_source}")
    else:
        exe_source = Path("dist/WhisperSpeechApp")
        if exe_source.exists():
            shutil.copytree(exe_source, dist_dir / "WhisperSpeechApp")
        else:
            safe_print(f"⚠️  Executable directory not found at {exe_source}")

    # Create README for distribution
    readme_content = f"""# Whisper Speech App - {system.title()} Distribution

## Installation

1. Extract this folder to your desired location
2. Run the application:
   - **macOS**: Double-click WhisperSpeechApp.app
   - **Windows**: Double-click WhisperSpeechApp.exe
   - **Linux**: Run ./WhisperSpeechApp

## First Run

The app will download Whisper models on first use (this may take a few minutes).

## Usage

1. The app runs in your system tray
2. Hold Fn key (or Cmd+Space) while speaking to record
3. Text will be automatically transcribed and pasted

## System Requirements

- **macOS**: macOS 10.14 or later
- **Windows**: Windows 10 or later
- **Linux**: Ubuntu 18.04 or equivalent

## Permissions

The app needs microphone access for speech recognition.

For more information, visit: https://github.com/suhanichawla/whisper-on-prem
"""

    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme_content)

    # Copy license and other files
    for file in ["README.md", "requirements.txt"]:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)

    # Create zip archive (remove existing zip first)
    zip_path = Path(f"distributions/{dist_name}.zip")
    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(f"distributions/{dist_name}", 'zip', dist_dir)

    safe_print(f"📦 Distribution package created: {dist_name}.zip")

def main():
    safe_print("🚀 Building Whisper Speech App Executables")
    safe_print("=" * 50)

    # Install PyInstaller
    install_pyinstaller()

    # Create spec file
    create_spec_file()

    # Build executable
    if build_executable():
        safe_print("\n✅ Build completed successfully!")
        safe_print("\n📋 Next steps:")
        safe_print("1. Test the executable in the 'dist' folder")
        safe_print("2. Upload the zip files from 'distributions' folder to your website")
        safe_print("3. Create a simple download page")
    else:
        safe_print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
