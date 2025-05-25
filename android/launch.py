#!/usr/bin/env python3
"""
TermiNote Android Launcher
Launch the TermiNote GUI app from Termux
"""

import os
import sys
from pathlib import Path

# Check if we're in Termux
if 'com.termux' in os.environ.get('PREFIX', ''):
    print("Launching TermiNote from Termux...")
else:
    print("Launching TermiNote...")

# Set up environment
os.environ['KIVY_WINDOW'] = 'sdl2'

# Import and run the main app
try:
    from main import TermiNoteApp
    TermiNoteApp().run()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required dependencies:")
    print("pip install kivy")
    sys.exit(1)
except Exception as e:
    print(f"Error launching app: {e}")
    sys.exit(1) 