#!/usr/bin/env python3

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def download_whisper_models():
    """Pre-download Whisper models to avoid delay on first use"""
    import whisper
    
    models_to_download = ["tiny", "base", "small"]  # Download smaller models first
    
    for model_name in models_to_download:
        print(f"Downloading Whisper {model_name} model...")
        try:
            whisper.load_model(model_name)
            print(f"✅ {model_name} model downloaded successfully")
        except Exception as e:
            print(f"❌ Failed to download {model_name} model: {e}")

def main():
    print("Setting up Local Speech-to-Text App...")
    
    # Install requirements
    install_requirements()
    
    # Download models
    print("\nDownloading Whisper models (this may take a few minutes)...")
    download_whisper_models()
    
    print("\n✅ Setup complete!")
    print("\nTo run the app:")
    print("python main.py")
    print("\nThe app will run in the system tray. Use Fn key (or Cmd+Space as fallback) to record speech.")

if __name__ == "__main__":
    main()