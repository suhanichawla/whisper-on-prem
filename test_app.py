#!/usr/bin/env python3

import subprocess
import time
import sys
import signal
import os

def test_app():
    """Test the Whisper app for basic functionality"""
    print("🧪 Testing Whisper Speech App...")

    try:
        # Start the app
        print("Starting the app...")
        process = subprocess.Popen(['python', 'main.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Let it run for a few seconds
        print("App running... (letting it initialize for 5 seconds)")
        time.sleep(5)

        # Check if process is still alive
        if process.poll() is None:
            print("✅ App is running successfully!")

            # Test graceful shutdown
            print("Testing graceful shutdown...")
            process.send_signal(signal.SIGTERM)

            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                print("✅ App shut down gracefully!")
                return True
            except subprocess.TimeoutExpired:
                print("⚠️ App didn't shut down gracefully, force killing...")
                process.kill()
                return False

        else:
            # Process died
            stdout, stderr = process.communicate()
            print("❌ App crashed during startup!")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_app()
    sys.exit(0 if success else 1)
