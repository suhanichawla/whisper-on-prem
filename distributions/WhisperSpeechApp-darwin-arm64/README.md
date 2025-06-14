# Local Speech-to-Text Desktop App

A privacy-focused desktop application that converts speech to text using OpenAI's Whisper models running locally on your machine. Perfect for companies that don't allow cloud-based speech recognition tools.

## Features

- 🎙️ **Local Processing**: All speech recognition happens on your device
- 🔄 **Multiple Whisper Models**: Choose from tiny, base, small, medium, or large models
- ⌨️ **Global Hotkey**: Hold Fn key (or Cmd+Space) to record
- 📋 **Auto-paste**: Automatically pastes transcribed text to active text field
- 🖥️ **System Tray**: Runs quietly in background
- 🎨 **Professional UI**: Clean PyQt6 interface

## Model Comparison

| Model  | Size | Speed | Accuracy | Use Case |
|--------|------|-------|----------|----------|
| tiny   | 39MB | Fastest | Basic | Quick notes, testing |
| base   | 74MB | Fast | Good | General use (recommended) |
| small  | 244MB | Medium | Better | Important transcriptions |
| medium | 769MB | Slow | High | Professional use |
| large  | 1550MB | Slowest | Best | Maximum accuracy needed |

## Installation

1. **Clone or download this project**
2. **Run setup script**:
   ```bash
   cd whisper-speech-app
   python setup.py
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

1. **Start the app** - It will appear in your system tray
2. **Configure model** - Choose your preferred Whisper model in the UI
3. **Record speech**:
   - Hold **Fn key** while speaking
   - Or use **Cmd+Space** as fallback
   - Or use the manual "Test Recording" button
4. **Get transcription**:
   - Text is automatically copied to clipboard
   - Text is automatically pasted to active text field
   - Text appears in the app window

## Hotkey Configuration

The app tries to detect the Fn key, but this can be system-dependent. Current fallbacks:
- **Primary**: Fn key (hardware level)
- **Fallback**: Cmd+Space (macOS) / Ctrl+Space (Windows/Linux)

## Changing Whisper Models

In the app interface:
1. Use the dropdown menu to select different models
2. Or modify the code in `main.py`:
   ```python
   self.current_model = "base"  # Change to: tiny, base, small, medium, large
   ```

## Requirements

- Python 3.8+
- PyQt6
- OpenAI Whisper
- PyAudio
- pynput

## Troubleshooting

### Audio Issues
- **macOS**: Grant microphone permissions in System Preferences > Security & Privacy
- **Windows**: Check Windows audio settings
- **Linux**: Install `portaudio19-dev` package

### Hotkey Issues
- If Fn key doesn't work, use Cmd+Space (macOS) or Ctrl+Space (Windows/Linux)
- Modify hotkey in `on_key_press()` method if needed

### Performance Issues
- Use smaller models (tiny/base) for faster processing
- Ensure sufficient RAM for larger models
- Close other intensive applications

## Privacy

- **100% Local**: No data sent to cloud services
- **No Internet Required**: Works completely offline (after initial model download)
- **Secure**: All processing happens on your machine

## License

MIT License - Feel free to modify and distribute