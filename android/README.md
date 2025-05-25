# TermiNote Android App

TermiNote v5 - AI Writing Assistant for Android devices. This is a standalone GUI app that can be run on Android through Termux or built as an APK.

## Features

- **Native Android GUI** - Touch-optimized interface built with Kivy
- **Writing Sessions** - Create, save, and manage multiple writing sessions
- **AI Integration** - Get writing suggestions and chat with AI (requires API key)
- **Export to Markdown** - Export your writing to the Downloads folder
- **Offline First** - Works without internet, AI features optional
- **Termux Compatible** - Run directly from Termux terminal

## Installation Methods

### Method 1: Run from Termux (Recommended)

1. **Install Termux** from F-Droid (not Google Play)
   ```bash
   # Download from: https://f-droid.org/packages/com.termux/
   ```

2. **Clone the repository**
   ```bash
   pkg install git
   git clone https://github.com/CVO-TreeAi/terminote.git
   cd terminote/android
   ```

3. **Run the installer**
   ```bash
   bash install-termux.sh
   ```

4. **Launch the app**
   ```bash
   terminote
   # Or from the android directory:
   python main.py
   ```

### Method 2: Manual Installation in Termux

1. **Install dependencies**
   ```bash
   pkg update
   pkg install python python-pip
   pkg install sdl2 sdl2-image sdl2-mixer sdl2-ttf
   pip install kivy pyyaml requests
   ```

2. **Run the app**
   ```bash
   cd terminote/android
   python main.py
   ```

### Method 3: Build APK (Advanced)

1. **On your development machine** (not in Termux):
   ```bash
   cd android
   python3.11 -m venv venv
   source venv/bin/activate
   pip install buildozer cython
   buildozer android debug
   ```

2. **Install the APK**
   ```bash
   adb install bin/terminote-*.apk
   ```

## Usage

### Main Menu
- **Start Writing** - Create a new writing session
- **Continue Session** - Resume a previous session
- **Sessions Manager** - View and manage all sessions
- **Settings** - Configure API key and preferences
- **Help** - View help and instructions

### Writing Screen
- **Save** - Save your current session
- **AI Help** - Get AI-powered suggestions
- **Export** - Export to markdown file
- **Chat Mode** - Toggle between writing and chat mode

### Sessions Manager
- View all saved sessions with word count
- Open any session to continue writing
- Delete sessions you no longer need

### Settings
- Configure your OpenRouter API key for AI features
- View app information

## File Locations

- **Sessions**: `~/.terminote/sessions/`
- **Config**: `~/.terminote/config.json`
- **Exports**: `/storage/emulated/0/Download/` (Android Downloads)

## Troubleshooting

### App won't start in Termux
```bash
# Set environment variables
export KIVY_WINDOW=sdl2
export KIVY_GL_BACKEND=gl

# Check Python version (should be 3.11+)
python --version

# Reinstall Kivy
pip uninstall kivy
pip install kivy
```

### Graphics issues
```bash
# Install all SDL2 dependencies
pkg install sdl2 sdl2-image sdl2-mixer sdl2-ttf python-numpy
```

### Permission issues
- Make sure Termux has storage permission
- Run: `termux-setup-storage`

### Can't find sessions
- Sessions are stored in `~/.terminote/sessions/`
- Check with: `ls ~/.terminote/sessions/`

## Development

### Project Structure
```
android/
├── main.py           # Main application
├── launch.py         # Simple launcher
├── buildozer.spec    # Build configuration
├── requirements.txt  # Python dependencies
├── install-termux.sh # Termux installer
└── README.md        # This file
```

### Running in Development
```bash
# With debug output
python main.py

# With Kivy debug
export KIVY_LOG_LEVEL=debug
python main.py
```

### Building for Release
```bash
buildozer android release
```

## Tips

1. **First Time Setup**
   - The app will create necessary directories on first run
   - Configure your API key in Settings for AI features

2. **Writing Tips**
   - Use Chat Mode to ask questions about your writing
   - Export regularly to backup your work
   - Sessions auto-save when you click Save

3. **Termux Tips**
   - Add `terminote` to your `.bashrc` for quick access
   - Use `termux-wake-lock` to prevent sleep during long sessions

## Requirements

- Android 5.0+ (API 21+)
- Termux (for terminal mode)
- Python 3.11+
- ~100MB storage space

## License

MIT License - See main repository for details

## Support

- GitHub Issues: https://github.com/CVO-TreeAi/terminote/issues
- Documentation: https://github.com/CVO-TreeAi/terminote/docs

---

Made with ❤️ by TreeAI 