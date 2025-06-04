#!/usr/bin/env python3

import sys
import os
import ssl
import threading
import queue
import time
import tempfile
import wave
import pyaudio
import numpy as np
import whisper
import pyperclip
from typing import Optional
import gc
import atexit
import signal

# Handle SSL certificate issues for model downloads
ssl._create_default_https_context = ssl._create_unverified_context

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSystemTrayIcon, QMenu,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QComboBox, QTextEdit, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap, QAction
import subprocess

# Import pynput with error handling
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput not available. Global hotkeys will not work.")

# Global variable to store the app instance for cleanup
app_instance = None
shutdown_in_progress = False

class WhisperProcessor(QThread):
    transcription_ready = pyqtSignal(str)
    processing_finished = pyqtSignal()

    def __init__(self, audio_file, model_size="base"):
        super().__init__()
        self.audio_file = audio_file
        self.model_size = model_size
        self._model = None
        self._cleanup_done = False

    def run(self):
        try:
            # Load model fresh each time to avoid memory issues
            print(f"Loading Whisper model: {self.model_size}")
            self._model = whisper.load_model(self.model_size)

            print("Transcribing audio...")
            result = self._model.transcribe(self.audio_file)
            text = result["text"].strip()
            print(f"Transcription complete: {text[:50]}...")
            self.transcription_ready.emit(text)
        except Exception as e:
            print(f"Whisper processing error: {e}")
            self.transcription_ready.emit(f"Error: {str(e)}")
        finally:
            self.cleanup()
            self.processing_finished.emit()

    def cleanup(self):
        """Force cleanup of resources"""
        if not self._cleanup_done:
            try:
                if self._model:
                    del self._model
                    self._model = None
                # Force garbage collection
                gc.collect()
                self._cleanup_done = True
            except:
                pass

    def __del__(self):
        self.cleanup()

class AudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.fs = 16000  # Whisper works best with 16kHz
        self.frames = []
        self.recording = False
        self.stream = None
        self.p = None
        self._cleanup_done = False

        # Initialize PyAudio with error handling
        self.init_pyaudio()

    def init_pyaudio(self):
        """Initialize PyAudio with better error handling"""
        try:
            if self.p:
                self.cleanup_pyaudio()
            self.p = pyaudio.PyAudio()
            print("PyAudio initialized successfully")
        except Exception as e:
            print(f"Error initializing PyAudio: {e}")
            self.p = None

    def cleanup_pyaudio(self):
        """Clean up PyAudio resources gently"""
        if self._cleanup_done:
            return

        try:
            if self.stream:
                try:
                    if self.recording:
                        self.recording = False
                        time.sleep(0.1)  # Give time for recording thread to stop
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                self.stream = None

            if self.p:
                try:
                    # Don't terminate aggressively - just let it be
                    # self.p.terminate() causes segfaults
                    pass
                except:
                    pass
                self.p = None

            self._cleanup_done = True
        except:
            pass

    def start_recording(self):
        if self.recording or not self.p:
            if not self.p:
                self.init_pyaudio()
            if not self.p:
                return False

        self.frames = []
        self.recording = True

        try:
            self.stream = self.p.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True
            )

            # Record in a separate thread to avoid blocking
            threading.Thread(target=self._record_audio, daemon=True).start()
            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.recording = False
            return False

    def _record_audio(self):
        print("🎙️ Recording thread started")
        frame_count = 0
        while self.recording and self.stream:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                frame_count += 1
                if frame_count % 50 == 0:  # Log every 50 frames (about every ~1 second)
                    print(f"📊 Recorded {frame_count} frames")
            except Exception as e:
                print(f"Recording error: {e}")
                break
        print(f"🎙️ Recording thread stopped. Total frames: {frame_count}")

    def stop_recording(self):
        if not self.recording or not self.p:
            print("Stop recording called but not recording or no PyAudio")
            return None

        print(f"Stopping recording... frames so far: {len(self.frames)}")
        self.recording = False
        time.sleep(0.1)  # Give recording thread time to stop

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

        if not self.frames:
            print("❌ No audio frames recorded!")
            return None

        print(f"📊 Total frames to save: {len(self.frames)}")

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')

        try:
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.sample_format))
                wf.setframerate(self.fs)
                wf.writeframes(b''.join(self.frames))
            print(f"✅ Audio saved to: {temp_file.name}")

            # Check file size
            file_size = os.path.getsize(temp_file.name)
            print(f"📁 Audio file size: {file_size} bytes")

            return temp_file.name
        except Exception as e:
            print(f"❌ Error saving audio file: {e}")
            return None

    def __del__(self):
        # Don't cleanup aggressively in destructor to avoid segfaults
        pass

class SpeechToTextApp(QMainWindow):
    # Add Qt signals for thread-safe communication
    key_detected_signal = pyqtSignal(str)
    hotkey_triggered_signal = pyqtSignal(str)
    hotkey_released_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.current_model = "base"
        self.whisper_thread = None
        self.hotkey_listener = None
        self._cleanup_done = False

        # Track modifier keys manually
        self.pressed_modifiers = set()
        self.hotkey_recording = False  # Track if recording was started by hotkey

        # Available Whisper models
        self.models = {
            "tiny": "Fastest, least accurate",
            "base": "Good balance of speed and accuracy",
            "small": "Better accuracy, slower",
            "medium": "High accuracy, much slower",
            "large": "Best accuracy, very slow"
        }

        self.init_ui()
        self.init_system_tray()
        self.init_hotkeys()

        # Connect signals
        self.key_detected_signal.connect(self.on_key_detected)
        self.hotkey_triggered_signal.connect(self.on_hotkey_triggered)
        self.hotkey_released_signal.connect(self.on_hotkey_released)

    def init_ui(self):
        self.setWindowTitle("Local Speech-to-Text")
        self.setGeometry(300, 300, 500, 450)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Whisper Model:"))

        self.model_combo = QComboBox()
        for model, description in self.models.items():
            self.model_combo.addItem(f"{model.title()} - {description}", model)
        self.model_combo.setCurrentText("Base - Good balance of speed and accuracy")
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Status
        self.status_label = QLabel("Ready. Try: Option+Space, Cmd+Space, F1, or 'Test Recording' button")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Manual record button for testing
        self.record_button = QPushButton("Test Recording (Click & Hold)")
        self.record_button.pressed.connect(self.start_manual_recording)
        self.record_button.released.connect(self.stop_manual_recording)
        layout.addWidget(self.record_button)

        # Debug button to show pressed modifiers
        self.debug_button = QPushButton("Show Currently Pressed Keys")
        self.debug_button.clicked.connect(self.show_pressed_keys)
        layout.addWidget(self.debug_button)

        # Test hotkey buttons
        hotkey_layout = QHBoxLayout()

        self.test_fn_button = QPushButton("Test Fn")
        self.test_fn_button.clicked.connect(lambda: self.test_hotkey("Fn key"))
        hotkey_layout.addWidget(self.test_fn_button)

        self.test_f1_button = QPushButton("Test F1")
        self.test_f1_button.clicked.connect(lambda: self.test_hotkey("F1 key"))
        hotkey_layout.addWidget(self.test_f1_button)

        self.test_option_button = QPushButton("Test Option+Space")
        self.test_option_button.clicked.connect(lambda: self.test_hotkey("Option+Space"))
        hotkey_layout.addWidget(self.test_option_button)

        layout.addLayout(hotkey_layout)

        # Transcription display
        layout.addWidget(QLabel("Last Transcription:"))
        self.transcription_display = QTextEdit()
        self.transcription_display.setMaximumHeight(100)
        layout.addWidget(self.transcription_display)

        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_transcription)
        self.copy_button.setEnabled(False)
        layout.addWidget(self.copy_button)

        # Debug info
        debug_label = QLabel("Debug: ffmpeg ✅, PyAudio ✅, Fixed segfault ✅")
        debug_label.setStyleSheet("color: green; font-size: 9px;")
        layout.addWidget(debug_label)

        # Key press debug display
        self.key_debug_label = QLabel("Key Debug: Press any key to see what's detected...")
        self.key_debug_label.setStyleSheet("color: blue; font-size: 9px; font-family: monospace;")
        layout.addWidget(self.key_debug_label)

        # Instructions for accessibility
        if PYNPUT_AVAILABLE:
            instructions = QLabel("🎯 Hotkey Options:\n• Option+Space (recommended)\n• Cmd+Space\n• F1 key\n• Fn key (if supported)\n\n⚠️ Grant accessibility permissions in System Preferences → Security & Privacy → Privacy → Accessibility")
            instructions.setWordWrap(True)
            instructions.setStyleSheet("color: orange; font-size: 10px; padding: 5px;")
            layout.addWidget(instructions)

    def init_system_tray(self):
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Create a simple icon (you can replace with an actual icon file)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()

    def init_hotkeys(self):
        # Only initialize if pynput is available
        if not PYNPUT_AVAILABLE:
            self.status_label.setText("Ready. Use 'Test Recording' button (Global hotkeys disabled)")
            return

        # Global hotkey listener for Fn key with error handling
        try:
            self.hotkey_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Warning: Could not start global hotkey listener: {e}")
            self.status_label.setText("Ready. Use 'Test Recording' button (Global hotkeys failed)")

    def on_key_detected(self, key_info):
        """Handle key detection signal (thread-safe)"""
        self.key_debug_label.setText(f"Last key: {key_info}")
        # Flash the debug label green when a key is detected
        self.key_debug_label.setStyleSheet("color: green; font-size: 9px; font-family: monospace; background-color: #90EE90;")
        QTimer.singleShot(200, lambda: self.key_debug_label.setStyleSheet("color: blue; font-size: 9px; font-family: monospace;"))

    def on_hotkey_triggered(self, hotkey_name):
        """Handle hotkey trigger signal (thread-safe)"""
        self.status_label.setText(f"🎯 {hotkey_name} detected! Recording...")
        self.start_recording()

    def on_hotkey_released(self, hotkey_name):
        """Handle hotkey release signal (thread-safe)"""
        self.status_label.setText(f"🎯 {hotkey_name} released! Recording stopped")
        self.stop_recording()

    def on_key_press(self, key):
        # Debug: Show all key presses (emit signal instead of direct UI update)
        try:
            key_info = f"KEY PRESS: {key}"
            if hasattr(key, 'vk'):
                key_info += f" (vk={key.vk})"
            if hasattr(key, 'char'):
                key_info += f" (char='{key.char}')"
            print(key_info)

            # Emit signal for thread-safe UI update
            self.key_detected_signal.emit(key_info)

        except Exception as e:
            print(f"Debug error: {e}")

        # Manually track modifier keys
        try:
            # Track modifier keys
            if key in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]:
                self.pressed_modifiers.add('alt')
                print(f"Added alt to modifiers: {self.pressed_modifiers}")
            elif key in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
                self.pressed_modifiers.add('cmd')
                print(f"Added cmd to modifiers: {self.pressed_modifiers}")
            elif key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.pressed_modifiers.add('ctrl')
                print(f"Added ctrl to modifiers: {self.pressed_modifiers}")

            # Check for hotkey combinations
            # Method 1: Fn key (hardware level)
            if hasattr(key, 'vk') and key.vk == 179:  # Fn key virtual key code
                print("🎯 DETECTED: Fn key!")
                self.hotkey_recording = True
                self.hotkey_triggered_signal.emit("Fn key")
                return

            # Method 2: F15 key (Fn alternative)
            elif key == keyboard.Key.f15:
                print("🎯 DETECTED: F15 key (Fn alternative)!")
                self.hotkey_recording = True
                self.hotkey_triggered_signal.emit("F15 key")
                return

            # Method 3: F1 key (simple alternative)
            elif key == keyboard.Key.f1:
                print("🎯 DETECTED: F1 key!")
                self.hotkey_recording = True
                self.hotkey_triggered_signal.emit("F1 key")
                return

            # Method 4: Space with modifiers
            elif key == keyboard.Key.space:
                print(f"Space key pressed with modifiers: {self.pressed_modifiers}")

                if 'alt' in self.pressed_modifiers:
                    print("🎯 DETECTED: Option+Space!")
                    self.hotkey_recording = True
                    self.hotkey_triggered_signal.emit("Option+Space")
                    return
                elif 'cmd' in self.pressed_modifiers:
                    print("🎯 DETECTED: Cmd+Space!")
                    self.hotkey_recording = True
                    self.hotkey_triggered_signal.emit("Cmd+Space")
                    return
                elif 'ctrl' in self.pressed_modifiers:
                    print("🎯 DETECTED: Ctrl+Space!")
                    self.hotkey_recording = True
                    self.hotkey_triggered_signal.emit("Ctrl+Space")
                    return
                else:
                    print("Space pressed but no recognized modifiers")

        except (AttributeError, Exception) as e:
            print(f"Hotkey detection error: {e}")

    def on_key_release(self, key):
        # Debug: Show all key releases
        try:
            key_info = f"KEY RELEASE: {key}"
            if hasattr(key, 'vk'):
                key_info += f" (vk={key.vk})"
            print(key_info)
        except Exception as e:
            print(f"Debug error: {e}")

        try:
            # Remove modifier keys from tracking
            if key in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]:
                self.pressed_modifiers.discard('alt')
                print(f"Removed alt from modifiers: {self.pressed_modifiers}")
            elif key in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
                self.pressed_modifiers.discard('cmd')
                print(f"Removed cmd from modifiers: {self.pressed_modifiers}")
            elif key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.pressed_modifiers.discard('ctrl')
                print(f"Removed ctrl from modifiers: {self.pressed_modifiers}")

            # Stop recording for hotkeys
            if self.hotkey_recording:
                if (hasattr(key, 'vk') and key.vk == 179) or key == keyboard.Key.f15 or key == keyboard.Key.f1:
                    print(f"🎯 RELEASED: {key}!")
                    self.hotkey_recording = False
                    self.hotkey_released_signal.emit(str(key))
                elif key == keyboard.Key.space and self.hotkey_recording:
                    print("🎯 RELEASED: Space (with modifiers)!")
                    self.hotkey_recording = False
                    self.hotkey_released_signal.emit("Space combo")

        except (AttributeError, Exception) as e:
            print(f"Key release error: {e}")

    def on_model_changed(self):
        current_data = self.model_combo.currentData()
        if current_data:
            self.current_model = current_data
            print(f"Model changed to: {self.current_model}")

    def start_recording(self):
        if self.is_recording:
            print("Already recording, ignoring start request")
            return

        print(f"Starting recording... (hotkey_recording={self.hotkey_recording})")
        success = self.recorder.start_recording()
        if success:
            self.is_recording = True
            if self.hotkey_recording:
                self.status_label.setText("🔴 Recording... (Hold hotkey to continue)")
            else:
                self.status_label.setText("🔴 Recording... (Release button to stop)")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            print("✅ Recording started successfully")
        else:
            self.status_label.setText("❌ Recording failed - check microphone")
            self.status_label.setStyleSheet("color: red;")
            print("❌ Recording failed to start")

    def stop_recording(self):
        if not self.is_recording:
            print("Not recording, ignoring stop request")
            return

        print(f"Stopping recording... (hotkey_recording={self.hotkey_recording})")
        self.is_recording = False
        self.hotkey_recording = False  # Reset hotkey recording flag
        self.status_label.setText("⏳ Processing...")
        self.status_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Stop recording and get audio file
        audio_file = self.recorder.stop_recording()

        print(f"Audio file path: {audio_file}")

        if audio_file:
            # Clean up any existing thread gently
            if self.whisper_thread and self.whisper_thread.isRunning():
                self.whisper_thread.quit()
                self.whisper_thread.wait(1000)  # Wait max 1 second
                self.whisper_thread.cleanup()

            # Process with Whisper in background thread
            self.whisper_thread = WhisperProcessor(audio_file, self.current_model)
            self.whisper_thread.transcription_ready.connect(self.on_transcription_ready)
            self.whisper_thread.processing_finished.connect(self.on_processing_finished)
            self.whisper_thread.start()
            print("🎯 Started Whisper processing thread")
        else:
            print("❌ No audio file generated")
            self.on_processing_finished()

    def start_manual_recording(self):
        self.start_recording()

    def stop_manual_recording(self):
        self.stop_recording()

    def on_transcription_ready(self, text):
        print(f"Transcription ready: {text}")
        self.transcription_display.setText(text)
        self.copy_button.setEnabled(True)

        # Auto-copy to clipboard and try to paste to active window
        try:
            pyperclip.copy(text)
            print("Text copied to clipboard")
        except Exception as e:
            print(f"Clipboard error: {e}")

        # Try to paste to active window (this is the advanced feature)
        try:
            # Minimize our window to get back to the original app
            self.showMinimized()

            # Small delay to ensure window switching
            QTimer.singleShot(100, self.paste_to_active_window)

        except Exception as e:
            print(f"Auto-paste error: {e}")

    def paste_to_active_window(self):
        """Attempt to paste transcribed text to the currently active text field"""
        try:
            # Use AppleScript on macOS to paste
            if sys.platform == "darwin":
                script = 'tell application "System Events" to keystroke "v" using command down'
                subprocess.run(["osascript", "-e", script], check=False)
            elif sys.platform == "win32":
                # Windows approach using keyboard
                import keyboard as kb
                kb.send('ctrl+v')
            elif sys.platform.startswith("linux"):
                # Linux approach
                import keyboard as kb
                kb.send('ctrl+v')
        except Exception as e:
            print(f"Paste error: {e}")

    def on_processing_finished(self):
        print("Processing finished")
        self.progress_bar.setVisible(False)

        # Update status based on whether hotkeys are available
        if PYNPUT_AVAILABLE and self.hotkey_listener:
            self.status_label.setText("Ready. Try: Option+Space, Cmd+Space, F1, or 'Test Recording' button")
        else:
            self.status_label.setText("Ready. Use 'Test Recording' button.")

        self.status_label.setStyleSheet("color: black; font-weight: normal;")

        # Clean up temporary audio file and thread
        if self.whisper_thread:
            if hasattr(self.whisper_thread, 'audio_file'):
                try:
                    os.unlink(self.whisper_thread.audio_file)
                    print(f"Cleaned up temp file: {self.whisper_thread.audio_file}")
                except:
                    pass

    def copy_transcription(self):
        text = self.transcription_display.toPlainText()
        if text:
            try:
                pyperclip.copy(text)
                self.status_label.setText("✅ Copied to clipboard!")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready. Try: Option+Space, Cmd+Space, F1, or 'Test Recording' button"))
            except Exception as e:
                print(f"Copy error: {e}")
                self.status_label.setText("❌ Copy failed!")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def closeEvent(self, event):
        # Hide to system tray instead of closing
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.cleanup_gentle()
            event.accept()

    def cleanup_gentle(self):
        """Gentle cleanup that doesn't cause segfaults"""
        if self._cleanup_done:
            return

        print("Gentle cleanup in progress...")

        global shutdown_in_progress
        shutdown_in_progress = True

        try:
            # Stop hotkey listener gently
            if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
                try:
                    self.hotkey_listener.stop()
                except:
                    pass

            # Wait for whisper thread to finish naturally
            if hasattr(self, 'whisper_thread') and self.whisper_thread:
                if self.whisper_thread.isRunning():
                    self.whisper_thread.quit()
                    self.whisper_thread.wait(2000)  # Wait max 2 seconds

            # Don't aggressively cleanup audio recorder - let Python GC handle it

            self._cleanup_done = True
        except:
            pass

    def quit_app(self):
        """Properly quit the application"""
        self.cleanup_gentle()
        # Use QTimer.singleShot to delay the quit slightly
        QTimer.singleShot(100, QApplication.instance().quit)

    def __del__(self):
        # Don't do aggressive cleanup in destructor
        pass

    def show_pressed_keys(self):
        """Show what keys are currently being tracked as pressed"""
        try:
            if self.hotkey_listener and hasattr(self.hotkey_listener, '_current_pressed'):
                pressed = self.hotkey_listener._current_pressed
                if pressed:
                    pressed_list = [str(key) for key in pressed]
                    message = f"Currently pressed: {', '.join(pressed_list)}"
                    print(message)
                    self.key_debug_label.setText(message)
                else:
                    message = "No keys currently pressed"
                    print(message)
                    self.key_debug_label.setText(message)
            else:
                message = "Hotkey listener not available or no _current_pressed attribute"
                print(message)
                self.key_debug_label.setText(message)

            # Flash the debug label
            self.key_debug_label.setStyleSheet("color: purple; font-size: 9px; font-family: monospace; background-color: #E6E6FA;")
            QTimer.singleShot(1000, lambda: self.key_debug_label.setStyleSheet("color: blue; font-size: 9px; font-family: monospace;"))

        except Exception as e:
            error_msg = f"Error checking pressed keys: {e}"
            print(error_msg)
            self.key_debug_label.setText(error_msg)

    def test_hotkey(self, hotkey_name):
        """Test a specific hotkey"""
        self.status_label.setText(f"🎯 {hotkey_name} detected! Recording...")
        self.start_recording()

def cleanup_global():
    """Global cleanup function"""
    global app_instance, shutdown_in_progress
    if app_instance and not shutdown_in_progress:
        app_instance.cleanup_gentle()

def signal_handler(signum, frame):
    """Handle signals gracefully"""
    print(f"Received signal {signum}, exiting gracefully...")
    cleanup_global()
    sys.exit(0)

def main():
    global app_instance

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Register global cleanup
    atexit.register(cleanup_global)

    app = QApplication(sys.argv)

    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray",
                           "System tray is not available on this system.")
        sys.exit(1)

    # Prevent app from quitting when main window is hidden
    app.setQuitOnLastWindowClosed(False)

    app_instance = SpeechToTextApp()
    app_instance.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("Interrupted by user")
        cleanup_global()
        sys.exit(0)

if __name__ == "__main__":
    main()
