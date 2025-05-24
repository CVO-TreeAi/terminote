#!/data/data/com.termux/files/usr/bin/bash
# TermiNote v5 - Simplified Termux Installation Script
# This script is specifically designed for Termux on Android

set -e

echo "🤖 TermiNote v5 - Termux Installation"
echo "======================================"

TERMINOTE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure we're in Termux
if [ -z "$TERMUX_VERSION" ]; then
    echo "❌ This script is designed for Termux only."
    echo "   Please use ./install.sh for other platforms."
    exit 1
fi

echo "📱 Installing for Termux on Android..."

# Check Python
if ! command -v python >/dev/null 2>&1; then
    echo "❌ Python not found. Installing..."
    pkg install -y python
fi

# Check git (for future updates)
if ! command -v git >/dev/null 2>&1; then
    echo "📦 Installing git..."
    pkg install -y git
fi

# Setup virtual environment
echo "🔧 Setting up virtual environment..."
if [ -d "$TERMINOTE_DIR/venv" ]; then
    rm -rf "$TERMINOTE_DIR/venv"
fi

python -m venv "$TERMINOTE_DIR/venv"
source "$TERMINOTE_DIR/venv/bin/activate"

# Install dependencies
echo "📥 Installing Python packages..."
pip install --upgrade pip
pip install -r "$TERMINOTE_DIR/requirements.txt"

# Create neo command directly
echo "📝 Creating neo command..."
cat > "$PREFIX/bin/neo" << EOF
#!/data/data/com.termux/files/usr/bin/bash
# NEO - TermiNote v5 launcher for Termux

TERMINOTE_DIR="$TERMINOTE_DIR"

# Always use the venv Python
export PATH="\$TERMINOTE_DIR/venv/bin:\$PATH"

cd "\$TERMINOTE_DIR"
source venv/bin/activate

# Check if first run
if [ ! -f ~/.terminote/config.yaml ] && [ "\$1" != "setup" ]; then
    echo "🔧 First time setup required..."
    python cli.py setup
    echo ""
fi

# Run TermiNote
if [ -z "\$1" ]; then
    python cli.py
else
    python cli.py "\$@"
fi
EOF

# Make executable
chmod +x "$PREFIX/bin/neo"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "   1. Run: neo setup"
echo "      (This will ask for your OpenRouter API key)"
echo ""
echo "   2. Then: neo"
echo "      (Start writing with NEO!)"
echo ""
echo "📖 Commands:"
echo "   neo              - Interactive menu"
echo "   neo write        - Start writing"
echo "   neo project      - Work on project"
echo "   neo --help       - Show all commands"
echo ""
echo "🔑 Get your API key at: https://openrouter.ai/keys"
EOF 