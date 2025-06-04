#!/bin/bash

echo "Starting Local Speech-to-Text App..."
echo ""
echo "⚠️  IMPORTANT: Grant accessibility permissions when prompted"
echo "   Go to: System Preferences → Security & Privacy → Privacy → Accessibility"
echo "   Add Terminal (or your terminal app) to the allowed list"
echo ""
echo "🎯 Hotkey Options (after granting permissions):"
echo "   • Option+Space - Hold while speaking (RECOMMENDED)"
echo "   • Cmd+Space - Hold while speaking (alternative)"
echo "   • F1 key - Hold while speaking (simple alternative)"
echo "   • Fn key - Hold while speaking (if supported by your Mac)"
echo ""
echo "📝 Manual Recording:"
echo "   - Use 'Test Recording' button (works immediately)"
echo "   - App runs in system tray when minimized"
echo ""

cd "$(dirname "$0")"
source venv/bin/activate
python main.py
