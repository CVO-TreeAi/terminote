#!/bin/bash
# TermiNote v5 Global Installation Script
# Creates a global 'neo' command for quick access to TermiNote

set -e

TERMINOTE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"

echo "🚀 Installing NEO (TermiNote v5) globally..."

# Check if virtual environment exists, create if not
if [ ! -d "$TERMINOTE_DIR/venv" ]; then
    echo "📦 Setting up virtual environment..."
    python3 -m venv "$TERMINOTE_DIR/venv"
    source "$TERMINOTE_DIR/venv/bin/activate"
    
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r "$TERMINOTE_DIR/requirements.txt"
    
    echo "✅ Virtual environment setup complete"
else
    echo "✅ Virtual environment already exists"
fi

# Create the neo command script
cat > /tmp/neo << 'EOF'
#!/bin/bash
# NEO - TermiNote v5 Quick Access Command

TERMINOTE_DIR="TERMINOTE_DIR_PLACEHOLDER"

# Function to show NEO banner
show_banner() {
    echo "╭─────────────────────────────────────────────╮"
    echo "│                    NEO v5                   │"
    echo "│         Your AI Writing Assistant          │"
    echo "╰─────────────────────────────────────────────╯"
    echo ""
}

# Function to quickly start a work session
quick_work() {
    show_banner
    echo "🎯 Quick Work Session"
    echo ""
    echo "1) 📝 Start writing"
    echo "2) 🏗️  Work on project" 
    echo "3) 📋 Continue last session"
    echo "4) ⚙️  Open full TermiNote"
    echo ""
    read -p "Choose (1-4): " choice
    
    case $choice in
        1) exec_terminote "write" ;;
        2) exec_terminote "project" ;;
        3) 
            # Find most recent session
            cd "$TERMINOTE_DIR"
            if [ -f venv/bin/activate ]; then
                source venv/bin/activate
                recent_session=$(python3 -c "
import json, os, glob
from pathlib import Path
sessions_dir = Path.home() / '.terminote' / 'sessions'
if sessions_dir.exists():
    sessions = list(sessions_dir.glob('*.json'))
    if sessions:
        latest = max(sessions, key=os.path.getmtime)
        with open(latest) as f:
            data = json.load(f)
        print(data.get('name', latest.stem))
" 2>/dev/null)
                if [ -n "$recent_session" ]; then
                    exec_terminote "write" "--session" "$recent_session"
                else
                    exec_terminote "write"
                fi
            else
                echo "❌ Virtual environment not found. Please run install.sh again."
                exit 1
            fi
            ;;
        4) exec_terminote "" ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
}

# Function to execute TermiNote commands
exec_terminote() {
    cd "$TERMINOTE_DIR"
    
    # Check if virtual environment exists
    if [ ! -f venv/bin/activate ]; then
        echo "❌ Virtual environment not found."
        echo "Please run: cd $TERMINOTE_DIR && ./install.sh"
        exit 1
    fi
    
    source venv/bin/activate
    
    # Check if setup is needed
    if [ ! -f ~/.terminote/config.yaml ] && [ "$1" != "setup" ]; then
        echo "🔧 First time setup required..."
        python3 cli.py setup
        echo ""
    fi
    
    if [ -z "$1" ]; then
        # Interactive mode
        python3 cli.py
    else
        python3 cli.py "$@"
    fi
}

# Main command handling
case "${1:-}" in
    "")
        # No arguments - show quick work menu
        quick_work
        ;;
    "work" | "w")
        # Quick work session
        quick_work
        ;;
    "write")
        exec_terminote "write" "${@:2}"
        ;;
    "project" | "p")
        exec_terminote "project" "${@:2}"
        ;;
    "generate" | "gen" | "g")
        exec_terminote "generate" "${@:2}"
        ;;
    "sessions" | "s")
        exec_terminote "sessions" "${@:2}"
        ;;
    "config" | "c")
        exec_terminote "config" "${@:2}"
        ;;
    "setup")
        exec_terminote "setup" "${@:2}"
        ;;
    "--help" | "-h" | "help")
        show_banner
        echo "NEO Commands:"
        echo ""
        echo "  neo                    Quick work menu"
        echo "  neo work               Quick work menu"
        echo "  neo write [session]    Start writing"
        echo "  neo project [name]     Work on project"
        echo "  neo generate <type>    Generate docs"
        echo "  neo sessions           List sessions"
        echo "  neo config             View config"
        echo "  neo setup              Initial setup"
        echo ""
        echo "Shortcuts:"
        echo "  neo w    = neo work"
        echo "  neo p    = neo project"
        echo "  neo g    = neo generate"
        echo "  neo s    = neo sessions"
        echo "  neo c    = neo config"
        echo ""
        ;;
    *)
        # Pass through to TermiNote
        exec_terminote "$@"
        ;;
esac
EOF

# Replace placeholder with actual directory
sed "s|TERMINOTE_DIR_PLACEHOLDER|$TERMINOTE_DIR|g" /tmp/neo > /tmp/neo_final

# Install the command
if [ "$EUID" -eq 0 ]; then
    # Running as root
    cp /tmp/neo_final "$INSTALL_DIR/neo"
    chmod +x "$INSTALL_DIR/neo"
    echo "✅ NEO installed globally to $INSTALL_DIR/neo"
else
    # Try with sudo
    echo "📋 Installing to $INSTALL_DIR requires admin privileges..."
    sudo cp /tmp/neo_final "$INSTALL_DIR/neo"
    sudo chmod +x "$INSTALL_DIR/neo"
    echo "✅ NEO installed globally to $INSTALL_DIR/neo"
fi

# Clean up
rm -f /tmp/neo /tmp/neo_final

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Quick start:"
echo "  neo setup        - Configure your OpenRouter API key"
echo "  neo              - Quick work menu"
echo "  neo write        - Start writing"
echo "  neo project      - Work on project"
echo ""
echo "Run 'neo --help' for full command list" 