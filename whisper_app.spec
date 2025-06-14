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