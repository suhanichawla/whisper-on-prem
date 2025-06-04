# Installation Complete! 🎉

Your local speech-to-text app is ready to use.

## ✅ What's Installed

- **PyQt6** - Modern UI framework  
- **Whisper Models** - Downloaded `tiny` (39MB) and `base` (74MB)
- **Audio System** - PyAudio with PortAudio for recording
- **Hotkey Detection** - Global key listener (pynput)

## 🚀 How to Run

```bash
cd /Users/schawla/Documents/personal/whisper-speech-app
./run.sh
```

**Or manually:**
```bash
source venv/bin/activate
python main.py
```

## 🔐 Permissions Required

**First time setup:**
1. Run the app: `./run.sh`
2. macOS will prompt for **Accessibility** permissions
3. Go to: **System Preferences → Security & Privacy → Privacy → Accessibility**
4. Add **Terminal** (or your terminal app) to allowed list
5. Restart the app

**Microphone permissions:**
- macOS will prompt automatically
- Grant microphone access when asked

## 🎙️ Usage

### Recording Methods:
1. **Fn Key** (primary) - Hold while speaking
2. **Cmd+Space** (fallback) - Hold while speaking  
3. **Manual Button** - Click & hold "Test Recording"

### Model Selection:
- **Tiny**: Fastest, basic accuracy (recommended for testing)
- **Base**: Good balance (recommended for daily use)
- **Small**: Better accuracy, slower (download needed)
- **Medium**: High accuracy, much slower (download needed)
- **Large**: Best accuracy, very slow (download needed)

### Output:
- Text automatically copies to clipboard
- Text automatically pastes to active text field
- Text appears in app window

## 🛠️ Advanced Configuration

### Change Hotkey
Edit `main.py` around line 200:
```python
# Current: Fn key or Cmd+Space
# Change to Ctrl+Shift:
if (key == keyboard.Key.space and 
    keyboard.Key.ctrl in pressed and 
    keyboard.Key.shift in pressed):
```

### Download More Models
```bash
source venv/bin/activate
python -c "
import ssl
import whisper
ssl._create_default_https_context = ssl._create_unverified_context
whisper.load_model('small')  # or 'medium', 'large'
"
```

### Change Default Model
Edit `main.py` line ~90:
```python
self.current_model = "base"  # Change to: tiny, small, medium, large
```

## 🐛 Troubleshooting

**"Not trusted" error:**
- Grant Accessibility permissions (see above)

**No audio recorded:**
- Check microphone permissions
- Try manual "Test Recording" button first

**SSL certificate errors:**
- Already handled with ssl workaround

**Hotkey not working:**
- Use Cmd+Space as fallback
- Try manual recording button
- Check Accessibility permissions

**App not pasting text:**
- Minimize app window to return focus to original app
- Check clipboard - text should still be copied

## 📁 Project Structure

```
whisper-speech-app/
├── venv/                  # Virtual environment
├── main.py               # Main application
├── requirements.txt      # Dependencies
├── run.sh               # Launch script
├── README.md            # Documentation
└── INSTALL.md           # This file
```

## 🎯 Performance Tips

- Use **tiny** model for fastest response
- Use **base** model for daily use
- Close other intensive apps when using larger models
- Models are cached after first load (faster subsequent use)

**Enjoy your privacy-focused speech-to-text app!** 🎤✨