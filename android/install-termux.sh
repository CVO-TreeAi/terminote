#!/data/data/com.termux/files/usr/bin/bash
# TermiNote Android Installation Script for Termux

echo "TermiNote v5 - Termux Installation"
echo "=================================="

# Update packages
echo "Updating Termux packages..."
pkg update -y

# Install Python and required system packages
echo "Installing Python and dependencies..."
pkg install -y python python-pip git

# Install SDL2 and other graphics dependencies for Kivy
echo "Installing graphics libraries..."
pkg install -y sdl2 sdl2-image sdl2-mixer sdl2-ttf
pkg install -y python-numpy

# Set up environment variables
export KIVY_WINDOW=sdl2
export KIVY_GL_BACKEND=gl

# Install Kivy and other Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install kivy pyyaml requests

# Create TermiNote directories
echo "Setting up TermiNote directories..."
mkdir -p ~/.terminote/sessions

# Create a launcher script in Termux bin
echo "Creating launcher script..."
cat > $PREFIX/bin/terminote << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
# TermiNote launcher for Termux

# Set environment
export KIVY_WINDOW=sdl2
export KIVY_GL_BACKEND=gl

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the android directory (either in current dir or in terminote repo)
if [ -f "./android/main.py" ]; then
    cd android
elif [ -f "$HOME/terminote/android/main.py" ]; then
    cd $HOME/terminote/android
elif [ -f "$HOME/Desktop/terminote/android/main.py" ]; then
    cd $HOME/Desktop/terminote/android
else
    echo "Error: Cannot find TermiNote android directory"
    echo "Please run from the terminote repository or install it first"
    exit 1
fi

# Launch the app
python main.py
EOF

chmod +x $PREFIX/bin/terminote

echo ""
echo "Installation complete!"
echo ""
echo "To run TermiNote, use one of these methods:"
echo "1. Type 'terminote' from anywhere in Termux"
echo "2. Navigate to the android directory and run: python main.py"
echo ""
echo "First time setup:"
echo "- The app will create ~/.terminote directory for sessions"
echo "- Configure your OpenRouter API key in Settings for AI features"
echo "" 