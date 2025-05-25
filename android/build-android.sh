#!/bin/bash
# TermiNote Android Build Script
# Builds the Android APK using Buildozer

set -e

echo "🤖 TermiNote Android App Builder"
echo "================================="

# Check if we're in the android directory
if [ ! -f "buildozer.spec" ]; then
    echo "❌ Error: buildozer.spec not found. Run this script from the android/ directory."
    exit 1
fi

# Check dependencies
echo "📋 Checking dependencies..."

# Check for buildozer
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer not found. Installing..."
    pip install buildozer cython
fi

# Check for Java
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install OpenJDK 17:"
    echo "   Ubuntu/Debian: sudo apt install openjdk-17-jdk"
    echo "   macOS: brew install openjdk@17"
    exit 1
fi

# Check Android SDK (buildozer will download if needed)
echo "✅ Dependencies check complete"

# Build modes
BUILD_MODE=${1:-debug}

case $BUILD_MODE in
    "debug")
        echo "🔨 Building DEBUG APK..."
        buildozer android debug
        ;;
    "release")
        echo "🔨 Building RELEASE APK..."
        echo "⚠️  Note: Release builds require signing keys"
        buildozer android release
        ;;
    "clean")
        echo "🧹 Cleaning build files..."
        buildozer android clean
        exit 0
        ;;
    *)
        echo "Usage: $0 [debug|release|clean]"
        echo ""
        echo "Examples:"
        echo "  $0 debug    - Build debug APK (default)"
        echo "  $0 release  - Build signed release APK"  
        echo "  $0 clean    - Clean build cache"
        exit 1
        ;;
esac

# Check if build was successful
if [ -f "bin/terminote-*-${BUILD_MODE}.apk" ]; then
    APK_FILE=$(ls bin/terminote-*-${BUILD_MODE}.apk | head -1)
    APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
    
    echo ""
    echo "✅ Build successful!"
    echo "📱 APK: $APK_FILE"
    echo "📦 Size: $APK_SIZE"
    echo ""
    echo "🚀 Installation options:"
    echo "1. Connect Android device and run: adb install $APK_FILE"
    echo "2. Transfer APK to device and install manually"
    echo "3. Upload to GitHub releases for distribution"
    echo ""
    
    # Auto-install if device connected
    if command -v adb &> /dev/null; then
        if adb devices | grep -q "device$"; then
            echo "📱 Android device detected!"
            read -p "Install APK now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "📥 Installing APK..."
                adb install -r "$APK_FILE"
                echo "✅ Installation complete!"
                echo "🎉 TermiNote is now installed on your device!"
            fi
        fi
    fi
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi 