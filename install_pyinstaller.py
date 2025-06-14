#!/usr/bin/env python3

import subprocess
import sys

def install_pyinstaller():
    """Install PyInstaller from public PyPI"""
    print("🔧 Installing PyInstaller from public PyPI...")

    commands_to_try = [
        # Standard installation from public PyPI
        [
            sys.executable, "-m", "pip", "install",
            "--index-url", "https://pypi.org/simple/",
            "--trusted-host", "pypi.org",
            "pyinstaller"
        ],
        # User installation
        [
            sys.executable, "-m", "pip", "install", "--user",
            "--index-url", "https://pypi.org/simple/",
            "--trusted-host", "pypi.org",
            "pyinstaller"
        ],
        # Force upgrade
        [
            sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall",
            "--index-url", "https://pypi.org/simple/",
            "--trusted-host", "pypi.org",
            "pyinstaller"
        ]
    ]

    for i, cmd in enumerate(commands_to_try, 1):
        try:
            print(f"📦 Attempt {i}: {' '.join(cmd[2:])}")
            subprocess.check_call(cmd)
            print("✅ PyInstaller installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Attempt {i} failed: {e}")
            if i < len(commands_to_try):
                print("🔄 Trying alternative method...")
            continue

    print("\n💡 All automatic installation attempts failed.")
    print("This is likely due to corporate network/pip configuration.")
    print("\n🔧 Manual Solutions:")
    print("1. Temporarily disable corporate pip config:")
    print("   pip config list  # see current config")
    print("   pip install --index-url https://pypi.org/simple/ pyinstaller")
    print("\n2. Use conda instead of pip:")
    print("   conda install pyinstaller")
    print("\n3. Download wheel manually from PyPI and install:")
    print("   # Visit https://pypi.org/project/pyinstaller/#files")
    print("   # Download appropriate .whl file")
    print("   # pip install downloaded_file.whl")

    return False

def test_installation():
    """Test if PyInstaller is properly installed"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller version {PyInstaller.__version__} is available")
        return True
    except ImportError:
        print("❌ PyInstaller is not available")
        return False

def main():
    print("🚀 PyInstaller Installation Helper")
    print("=" * 40)

    # Check if already installed
    if test_installation():
        print("✅ PyInstaller is already installed!")
        return

    # Try to install
    if install_pyinstaller():
        # Test the installation
        test_installation()
    else:
        print("\n📖 See above for manual installation options")

if __name__ == "__main__":
    main()
