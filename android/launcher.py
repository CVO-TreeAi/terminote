#!/usr/bin/env python3
"""
TermiNote Dual-Mode Launcher
Automatically detects environment and launches appropriate interface:
- Android: GUI app (Kivy)
- Terminal/Termux: CLI interface
- Termux with GUI: Option to choose
"""

import os
import sys
import platform
from pathlib import Path

# Add parent directory to path for importing TermiNote modules
app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root))

def detect_environment():
    """Detect the runtime environment and return appropriate mode."""
    
    # Check if running on Android
    is_android = hasattr(sys, 'getandroidapilevel')
    is_termux = 'TERMUX_VERSION' in os.environ
    
    # Check if GUI is available
    gui_available = False
    try:
        import kivy
        gui_available = True
    except ImportError:
        pass
    
    # Check if we're in a terminal
    is_terminal = sys.stdin.isatty() and sys.stdout.isatty()
    
    return {
        'android': is_android,
        'termux': is_termux,
        'gui_available': gui_available,
        'terminal': is_terminal,
        'platform': platform.system()
    }

def launch_gui_app():
    """Launch the Kivy GUI application."""
    try:
        from main import TermiNoteApp
        print("🚀 Starting TermiNote GUI...")
        TermiNoteApp().run()
    except ImportError as e:
        print(f"❌ GUI not available: {e}")
        print("💡 Install GUI dependencies: pip install kivy kivymd")
        return False
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        return False
    return True

def launch_terminal_app():
    """Launch the terminal CLI application."""
    try:
        # Import and run the CLI
        from cli import cli
        print("⌨️  Starting TermiNote CLI...")
        cli()
    except ImportError as e:
        print(f"❌ CLI not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting CLI: {e}")
        return False
    return True

def show_mode_selection():
    """Show mode selection menu when both options are available."""
    print("\n╭─────────────────────────────────────╮")
    print("│          TermiNote v5 Launcher      │")
    print("╰─────────────────────────────────────╯")
    print("")
    print("Select interface mode:")
    print("1) 📱 GUI App (Touch-friendly)")
    print("2) ⌨️  Terminal CLI (Keyboard-focused)")
    print("3) ❓ Auto-detect")
    print("")
    
    while True:
        try:
            choice = input("Choose (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return choice
            print("Invalid choice. Please select 1, 2, or 3.")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            sys.exit(0)

def main():
    """Main launcher function."""
    env = detect_environment()
    
    # Force mode from command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode in ['gui', 'app', 'kivy']:
            if env['gui_available']:
                return launch_gui_app()
            else:
                print("❌ GUI mode not available")
                return False
        elif mode in ['cli', 'terminal', 'console']:
            return launch_terminal_app()
        elif mode in ['help', '--help', '-h']:
            print("TermiNote Launcher")
            print("Usage: launcher.py [mode]")
            print("")
            print("Modes:")
            print("  gui      Launch GUI app")
            print("  cli      Launch terminal CLI")
            print("  help     Show this help")
            print("")
            print("Without arguments, auto-detects best mode")
            return True
    
    # Environment-based auto-detection
    print(f"🔍 Detected: {env['platform']}")
    
    if env['android'] and not env['termux']:
        # Pure Android environment - prefer GUI
        print("📱 Android device detected - launching GUI app")
        return launch_gui_app()
    
    elif env['termux']:
        # Termux environment - check capabilities
        if env['gui_available'] and env['terminal']:
            # Both available - let user choose
            print("🤖 Termux with GUI support detected")
            choice = show_mode_selection()
            
            if choice == '1':
                return launch_gui_app()
            elif choice == '2':
                return launch_terminal_app()
            else:  # Auto-detect
                # In Termux, prefer terminal if stdin/stdout available
                if env['terminal']:
                    print("🎯 Auto-selected: Terminal CLI")
                    return launch_terminal_app()
                else:
                    print("🎯 Auto-selected: GUI App")
                    return launch_gui_app()
        
        elif env['gui_available']:
            print("🤖 Termux GUI mode - launching GUI app")
            return launch_gui_app()
        else:
            print("🤖 Termux terminal mode - launching CLI")
            return launch_terminal_app()
    
    else:
        # Desktop/server environment
        if env['gui_available'] and not env['terminal']:
            # GUI available but not in terminal (e.g., launched from desktop)
            print("🖥️  Desktop GUI mode - launching GUI app")
            return launch_gui_app()
        else:
            # Terminal environment (most common for CLI tools)
            print("⌨️  Terminal environment - launching CLI")
            return launch_terminal_app()

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n💡 Troubleshooting:")
        print("- For GUI: pip install kivy kivymd")
        print("- For CLI: pip install click rich openai")
        print("- Check dependencies: python -m pip list")
        sys.exit(1) 