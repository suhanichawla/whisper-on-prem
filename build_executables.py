#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            # Try installing from public PyPI (workaround for corporate environments)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--index-url", "https://pypi.org/simple/",
                "--trusted-host", "pypi.org",
                "pyinstaller"
            ])
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install from public PyPI, trying alternative...")
            try:
                # Alternative: try with --user flag
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--user",
                    "--index-url", "https://pypi.org/simple/",
                    "--trusted-host", "pypi.org",
                    "pyinstaller"
                ])
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install PyInstaller: {e}")
                print("\n🔧 Manual installation required:")
                print("Try running one of these commands:")
                print("  pip install --index-url https://pypi.org/simple/ pyinstaller")
                print("  pip install --user --index-url https://pypi.org/simple/ pyinstaller")
                print("  python -m pip install --upgrade --index-url https://pypi.org/simple/ pyinstaller")
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
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    print(f"🏗️ Building executable for {system}...")

    try:
        # Clean previous builds
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('build'):
            shutil.rmtree('build')

        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "whisper_app.spec", "--clean"]
        subprocess.check_call(cmd)

        print("✅ Executable built successfully!")
        print(f"📁 Output location: {os.path.abspath('dist')}")

        # Create distribution folder
        create_distribution_package(system)

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

    return True

def create_distribution_package(system):
    """Create a complete distribution package"""
    dist_name = f"WhisperSpeechApp-{system}-{platform.machine()}"
    dist_dir = Path(f"distributions/{dist_name}")

    # Create distribution directory
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Copy built application
    if system == "darwin":
        app_source = Path("dist/WhisperSpeechApp.app")
        if app_source.exists():
            shutil.copytree(app_source, dist_dir / "WhisperSpeechApp.app")
    else:
        exe_source = Path("dist/WhisperSpeechApp")
        if exe_source.exists():
            shutil.copytree(exe_source, dist_dir / "WhisperSpeechApp")

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

For more information, visit: https://github.com/yourusername/whisper-speech-app
"""

    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme_content)

    # Copy license and other files
    for file in ["README.md", "requirements.txt"]:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)

    # Create zip archive
    archive_name = f"{dist_name}.zip"
    shutil.make_archive(f"distributions/{dist_name}", 'zip', dist_dir)

    print(f"📦 Distribution package created: {archive_name}")

def main():
    print("🚀 Building Whisper Speech App Executables")
    print("=" * 50)

    # Install PyInstaller
    install_pyinstaller()

    # Create spec file
    create_spec_file()

    # Build executable
    if build_executable():
        print("\n✅ Build completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the executable in the 'dist' folder")
        print("2. Upload the zip files from 'distributions' folder to your website")
        print("3. Create a simple download page")
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
