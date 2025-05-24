#!/bin/bash
# TermiNote v5 Activation Script
# Usage: source terminote.sh

# Get the directory where this script is located
TERMINOTE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the virtual environment
source "$TERMINOTE_DIR/venv/bin/activate"

# Create an alias for easy access
alias terminote="python3 '$TERMINOTE_DIR/cli.py'"

# Optional: Add to PATH for global access
export PATH="$TERMINOTE_DIR:$PATH"

echo "🚀 TermiNote v5 activated!"
echo "📝 Usage:"
echo "   terminote setup       - Initial setup (API keys, preferences)"
echo "   terminote write        - Start writing session"
echo "   terminote project      - Start project planning"
echo "   terminote generate     - Generate documentation"
echo "   terminote sessions     - Manage sessions"
echo "   terminote config       - View configuration"
echo ""
echo "💡 Run 'terminote --help' for full command list" 