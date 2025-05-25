#!/bin/bash
# TermiNote Android Development Installation Script
# Sets up development environment for building Android APKs

set -e

echo "🤖 TermiNote Android Development Setup"
echo "======================================"
echo ""

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    echo "⚠️  Platform $OSTYPE not fully supported, but will try..."
    PLATFORM="Unknown"
fi

echo "🔍 Platform: $PLATFORM"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    echo ""
    if [[ "$PLATFORM" == "macOS" ]]; then
        echo "macOS: brew install python3"
    elif [[ "$PLATFORM" == "Linux" ]]; then
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    fi
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check Java
if ! command -v java &> /dev/null; then
    echo "🔧 Installing OpenJDK 17..."
    if [[ "$PLATFORM" == "macOS" ]]; then
        if command -v brew &> /dev/null; then
            brew install openjdk@17
            echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
        else
            echo "❌ Homebrew not found. Please install Java manually:"
            echo "https://adoptium.net/temurin/releases/"
            exit 1
        fi
    elif [[ "$PLATFORM" == "Linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y openjdk-17-jdk
        elif command -v yum &> /dev/null; then
            sudo yum install -y java-17-openjdk-devel
        else
            echo "❌ Package manager not supported. Please install OpenJDK 17 manually."
            exit 1
        fi
    fi
else
    echo "✅ Java found: $(java -version 2>&1 | head -n 1)"
fi

# Setup Python virtual environment
echo ""
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install base TermiNote dependencies
echo ""
echo "📥 Installing TermiNote dependencies..."
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
else
    # Fallback dependencies
    pip install click rich openai pyyaml python-dotenv prompt_toolkit markdown-it-py tqdm
fi

# Install Android build dependencies
echo ""
echo "🤖 Installing Android build dependencies..."
pip install buildozer cython

# Install Kivy for GUI
echo ""
echo "🖥️  Installing GUI dependencies..."
pip install kivy kivymd

# Install Android development tools (if not already present)
echo ""
echo "🛠️  Checking Android development tools..."

# ADB (Android Debug Bridge)
if ! command -v adb &> /dev/null; then
    echo "🔧 Installing ADB..."
    if [[ "$PLATFORM" == "macOS" ]]; then
        if command -v brew &> /dev/null; then
            brew install android-platform-tools
        else
            echo "⚠️  ADB not found. Install manually for device testing."
        fi
    elif [[ "$PLATFORM" == "Linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt install -y android-tools-adb
        else
            echo "⚠️  ADB not found. Install manually for device testing."
        fi
    fi
else
    echo "✅ ADB found"
fi

# Make scripts executable
echo ""
echo "🔧 Setting up build scripts..."
chmod +x build-android.sh
chmod +x launcher.py

# Create .gitignore for build artifacts
cat > .gitignore << EOF
# Buildozer files
.buildozer/
bin/
build/

# Virtual environment
venv/

# Python cache
__pycache__/
*.pyc
*.pyo

# Android
*.apk
*.aab
*.keystore

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ Build environment configured"

# Test installation
echo ""
echo "🧪 Testing installation..."

# Test basic imports
python3 -c "
import kivy
import buildozer
from pathlib import Path
import sys
sys.path.append('..')
from core.session import SessionManager
print('✅ All imports successful')
"

echo ""
echo "🎉 Android development environment setup complete!"
echo ""
echo "📋 What you can do now:"
echo ""
echo "🔨 Build APK:"
echo "   ./build-android.sh debug    # Debug APK"
echo "   ./build-android.sh release  # Release APK"
echo ""
echo "🧪 Test locally:"
echo "   python3 launcher.py         # Auto-detect mode"
echo "   python3 launcher.py gui     # Force GUI mode"
echo "   python3 launcher.py cli     # Force CLI mode"
echo ""
echo "📱 Install on device:"
echo "   1. Enable Developer Options & USB Debugging"
echo "   2. Connect device via USB"
echo "   3. Run: adb install bin/terminote-*-debug.apk"
echo ""
echo "🚀 Build and install in one step:"
echo "   ./build-android.sh debug    # Will offer to auto-install"
echo ""

# Show environment info
echo "📊 Environment Summary:"
echo "   Platform: $PLATFORM"
echo "   Python: $(python3 --version)"
echo "   Java: $(java -version 2>&1 | head -n 1 | cut -d'"' -f2)"
echo "   Buildozer: $(buildozer version 2>/dev/null || echo 'Installed')"
echo "   ADB: $(command -v adb &> /dev/null && echo 'Available' || echo 'Not found')"
echo ""
echo "💡 Next steps:"
echo "   1. Configure your OpenRouter API key: python3 ../cli.py setup"
echo "   2. Test the app: python3 launcher.py"
echo "   3. Build APK: ./build-android.sh debug"
echo "" 