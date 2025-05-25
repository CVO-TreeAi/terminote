# TermiNote Android App

**Native Android application with dual-mode support (GUI + Terminal)**

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/CVO-TreeAi/terminote/releases)
[![Platform](https://img.shields.io/badge/platform-Android%205.0%2B-green.svg)](#compatibility)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)

## 🚀 **Features**

### **📱 Native Android App**
- **Touch-optimized interface** with large buttons and scrollable text areas
- **Material Design** inspired UI with dark/light theme support
- **Session management** with visual session browser
- **Export to Downloads** folder with one-tap sharing
- **Background writing** with auto-save and session recovery

### **⌨️ Dual-Mode Support**
- **GUI Mode**: Touch-friendly interface for phone/tablet use
- **Terminal Mode**: Full CLI interface for Termux users
- **Auto-detection**: Intelligently chooses best mode for environment
- **Manual override**: Force specific mode with command-line arguments

### **🤖 AI Integration**
- **Chat toggle**: Switch between writing and AI chat seamlessly
- **Context-aware AI**: AI understands your entire document
- **Writing assistance**: Get suggestions, continuations, and feedback
- **Offline capable**: Local session storage works without internet

## 📦 **Installation Options**

### **Option 1: Install from GitHub Releases**
```bash
# Download latest APK
wget https://github.com/CVO-TreeAi/terminote/releases/latest/download/terminote-release.apk

# Install on connected device
adb install terminote-release.apk
```

### **Option 2: Build from Source**
```bash
# Clone repository
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote/android

# Setup development environment
./install-android-dev.sh

# Build APK
./build-android.sh debug

# Install (device connected via USB)
adb install bin/terminote-*-debug.apk
```

### **Option 3: Termux Terminal (No APK needed)**
```bash
# Install in Termux
pkg install python git
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote
./install-termux.sh

# Launch with GUI option
python android/launcher.py
```

## 🔧 **Development Setup**

### **Prerequisites**
- **Python 3.8+** with pip
- **Java 17** (OpenJDK recommended)
- **Android SDK** (auto-downloaded by Buildozer)
- **Git** for source control

### **macOS Setup**
```bash
# Install dependencies
brew install python3 openjdk@17 android-platform-tools

# Clone and setup
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote/android
./install-android-dev.sh
```

### **Linux Setup**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip openjdk-17-jdk android-tools-adb

# Clone and setup
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote/android
./install-android-dev.sh
```

### **Build Commands**
```bash
# Debug build (unsigned, for testing)
./build-android.sh debug

# Release build (requires signing)
./build-android.sh release

# Clean build cache
./build-android.sh clean
```

## 📱 **App Interface Guide**

### **Welcome Screen**
- **Start Writing**: Create new session and begin writing
- **Continue Session**: Browse and open existing sessions
- **Project Mode**: Work on long-form projects with planning
- **Sessions Manager**: View all sessions with metadata
- **Settings**: Configure API key and preferences

### **Writing Screen**
```
┌─────────────────────────────────────┐
│ Session: My Story        💬│← Back │
├─────────────────────────────────────┤
│                                     │
│ [Large scrollable text area for     │
│  writing content with soft          │
│  keyboard support]                  │
│                                     │
├─────────────────────────────────────┤
│ 💾 Save │ 🤖 AI Help │ 📤 Export   │
└─────────────────────────────────────┘
```

### **Chat Mode Toggle**
- **💬 Chat Mode**: Ask AI questions about your writing
- **✍️ Write Mode**: Return to focused writing
- **Seamless switching**: Context preserved between modes

### **Sessions Browser**
- **Visual list** of all sessions with metadata
- **Word count** and last modified date
- **One-tap open** or delete operations
- **Search and filter** capabilities (planned)

## 🤖 **AI Features**

### **Writing Assistance**
```python
# Example AI interactions
"Can you help me improve this paragraph?"
"What would be a good ending for this story?"
"Check my grammar and style"
"Continue this section in the same tone"
```

### **Context Awareness**
- AI has access to your **entire document**
- Maintains **conversation history** in chat mode
- Understands **document structure** and purpose
- Provides **relevant suggestions** based on content

### **Offline Capability**
- **Sessions stored locally** on device
- **No internet required** for basic writing
- **Background sync** when connection available
- **Export capabilities** work offline

## 📄 **File Management**

### **Session Storage**
- **Location**: `/storage/emulated/0/Android/data/ai.treeai.terminote/files/.terminote/sessions/`
- **Format**: JSON files with metadata
- **Backup**: Automatic .bak files on save
- **Recovery**: Built-in corruption recovery

### **Export Options**
```bash
# Available export formats
- Markdown (.md)     # Default format
- Plain text (.txt)  # Simple text
- Rich text (.rtf)   # With formatting
- PDF (.pdf)         # Formatted document
```

### **Sharing Integration**
- **Share via any app** (Email, Drive, Slack, etc.)
- **Copy to clipboard** for quick sharing
- **Save to Downloads** for easy access
- **Cloud sync** via third-party apps

## 🔐 **Privacy & Security**

### **Data Storage**
- **Local storage only** - no cloud by default
- **Encrypted API keys** in secure Android keystore
- **User-controlled exports** - you choose what to share
- **No telemetry** or usage tracking

### **Network Usage**
- **Only for AI features** when explicitly requested
- **No background data** transmission
- **Configurable API endpoints** for self-hosted models
- **Offline mode** available for privacy-conscious users

## 🐛 **Troubleshooting**

### **Common Issues**

**App won't start:**
```bash
# Check device compatibility
adb shell getprop ro.build.version.sdk  # Should be 21+

# Check installed apps
adb shell pm list packages | grep terminote

# View app logs
adb logcat | grep TermiNote
```

**Build failures:**
```bash
# Clean build environment
./build-android.sh clean
rm -rf .buildozer/

# Update buildozer
pip install --upgrade buildozer

# Check Java version
java -version  # Should be 17+
```

**GUI not working:**
```bash
# Test dependencies
python3 -c "import kivy; print('Kivy OK')"

# Force terminal mode
python3 launcher.py cli

# Check for missing libs
adb logcat | grep -i "not found"
```

### **Performance Optimization**

**Large documents:**
- Use **session splitting** for documents >50k words
- Enable **auto-save** to prevent data loss
- Consider **project mode** for multi-chapter works

**Battery optimization:**
- **Disable background app refresh** if not needed
- Use **airplane mode + Wi-Fi** for distraction-free writing
- **Auto-brightness** saves battery during long sessions

## 🔄 **Dual-Mode Architecture**

### **Environment Detection**
```python
def detect_environment():
    is_android = hasattr(sys, 'getandroidapilevel')
    is_termux = 'TERMUX_VERSION' in os.environ
    gui_available = can_import('kivy')
    terminal = sys.stdin.isatty()
    
    # Auto-select appropriate interface
    if is_android and not is_termux:
        return 'gui'  # Native Android app
    elif is_termux and gui_available:
        return 'choose'  # Let user decide
    else:
        return 'cli'  # Terminal interface
```

### **Mode Switching**
```bash
# Force specific mode
python3 launcher.py gui      # GUI mode
python3 launcher.py cli      # Terminal mode

# Auto-detect (default)
python3 launcher.py          # Best mode for environment
```

## 🚀 **Deployment**

### **GitHub Releases**
```bash
# Build release APK
./build-android.sh release

# Create GitHub release
gh release create v5.0.0 \
  bin/terminote-5.0.0-release.apk \
  --title "TermiNote v5.0.0 Android App" \
  --notes "Native Android app with dual-mode support"
```

### **F-Droid Distribution**
- **Open source compatible** - no proprietary dependencies
- **Reproducible builds** with buildozer configuration
- **Metadata** included for F-Droid inclusion

### **Direct Installation**
```bash
# Enable unknown sources in Android Settings
# Settings > Security > Unknown Sources

# Download and install APK
# OR scan QR code from GitHub releases
```

## 📊 **Compatibility**

### **Android Versions**
- **Minimum**: Android 5.0 (API 21)
- **Target**: Android 13 (API 33)
- **Tested on**: Android 7.0 - 14.0
- **Architectures**: ARM64, ARMv7, x86_64

### **Device Types**
- **📱 Phones**: 4.5" - 6.8" screens optimized
- **📲 Tablets**: 7" - 12" with expanded layouts
- **🤖 Termux**: Full CLI compatibility
- **📦 Chrome OS**: Android app support

### **Hardware Requirements**
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 50MB app + session storage
- **Network**: Optional for AI features
- **Keyboard**: On-screen or physical supported

## 🎯 **Roadmap**

### **v5.1 (Next Release)**
- [ ] **Voice input** integration with speech-to-text
- [ ] **Handwriting support** for stylus input
- [ ] **Split-screen mode** for research and writing
- [ ] **Widget** for quick note capture

### **v5.2 (Future)**
- [ ] **Real-time collaboration** for shared documents
- [ ] **Advanced export** with custom templates
- [ ] **Plugin system** for custom AI models
- [ ] **Wear OS companion** app

---

## 🤝 **Contributing**

We welcome contributions to the Android app! See our [Contributing Guide](../CONTRIBUTING.md) for details.

### **Android-Specific Development**
- **UI/UX improvements** in Kivy framework
- **Android-specific features** (notifications, widgets, etc.)
- **Performance optimizations** for mobile devices
- **Platform integration** (sharing, file access, etc.)

### **Testing**
- **Device testing** on various Android versions
- **Performance profiling** with large documents
- **Battery usage optimization**
- **Accessibility compliance**

---

**TermiNote Android App - Writing reimagined for mobile** 📱✍️🤖 