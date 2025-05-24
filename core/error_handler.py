"""
Centralized error handling for TermiNote v5
Provides consistent error handling across platforms with specific support for macOS and Android/Termux.
"""

import os
import sys
import traceback
import platform
from pathlib import Path
from typing import Optional, Callable, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class TermiNoteError(Exception):
    """Base exception for TermiNote-specific errors."""
    pass

class ConfigurationError(TermiNoteError):
    """Raised when configuration is invalid or missing."""
    pass

class APIError(TermiNoteError):
    """Raised when API operations fail."""
    pass

class SessionError(TermiNoteError):
    """Raised when session operations fail."""
    pass

class PlatformError(TermiNoteError):
    """Raised when platform-specific operations fail."""
    pass

class ErrorHandler:
    """Centralized error handling with platform-specific support."""
    
    def __init__(self):
        self.is_termux = 'TERMUX_VERSION' in os.environ
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.debug_mode = os.environ.get('TERMINOTE_DEBUG', '').lower() in ('1', 'true', 'yes')
    
    def handle_error(self, error: Exception, context: str = "", user_message: str = None) -> bool:
        """
        Handle an error with appropriate user feedback.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            user_message: Custom user-friendly message
            
        Returns:
            bool: True if error was handled gracefully, False if critical
        """
        error_type = type(error).__name__
        
        # Determine severity and user message
        if isinstance(error, (ConfigurationError, APIError)):
            severity = "warning"
            is_critical = False
        elif isinstance(error, (SessionError, PlatformError)):
            severity = "error"
            is_critical = False
        else:
            severity = "critical"
            is_critical = True
        
        # Get platform-specific guidance
        platform_guidance = self._get_platform_guidance(error)
        
        # Display error to user
        self._display_error(error, context, user_message, severity, platform_guidance)
        
        # Log for debugging if enabled
        if self.debug_mode:
            self._log_error(error, context)
        
        return not is_critical
    
    def _display_error(self, error: Exception, context: str, user_message: str, 
                      severity: str, platform_guidance: str):
        """Display error to user with rich formatting."""
        
        # Color scheme based on severity
        colors = {
            "warning": "yellow",
            "error": "red", 
            "critical": "bold red"
        }
        color = colors.get(severity, "red")
        
        # Error icons
        icons = {
            "warning": "⚠️ ",
            "error": "❌",
            "critical": "💥"
        }
        icon = icons.get(severity, "❌")
        
        # Build error message
        if user_message:
            message = user_message
        else:
            message = str(error)
        
        error_content = f"[{color}]{icon} {message}[/{color}]"
        
        if context:
            error_content += f"\n[dim]Context: {context}[/dim]"
        
        if platform_guidance:
            error_content += f"\n\n[cyan]💡 Platform-specific help:[/cyan]\n{platform_guidance}"
        
        # Add general troubleshooting for critical errors
        if severity == "critical":
            error_content += self._get_troubleshooting_guide()
        
        console.print(Panel(
            error_content,
            title=f"{icon} TermiNote Error",
            border_style=color
        ))
    
    def _get_platform_guidance(self, error: Exception) -> str:
        """Get platform-specific guidance for common errors."""
        error_msg = str(error).lower()
        
        # Permission errors
        if "permission denied" in error_msg:
            if self.is_termux:
                return "• On Termux: Check storage permissions\n• Run: termux-setup-storage"
            elif self.is_macos:
                return "• On macOS: Try with sudo or check file permissions\n• Ensure Terminal has disk access in System Preferences"
            else:
                return "• Check file permissions\n• Try with appropriate privileges"
        
        # Network/API errors
        if any(x in error_msg for x in ["connection", "network", "api", "openrouter"]):
            base_guide = "• Check internet connection\n• Verify API key at https://openrouter.ai/keys"
            if self.is_termux:
                return base_guide + "\n• On Termux: Check if Termux has network permission"
            return base_guide
        
        # File not found errors
        if "no such file" in error_msg or "file not found" in error_msg:
            if self.is_termux:
                return "• On Termux: Files might be in /data/data/com.termux/files/home/\n• Use full paths or check working directory"
            return "• Check file path and permissions\n• Ensure the file exists"
        
        # Virtual environment errors
        if "venv" in error_msg or "virtual" in error_msg:
            base_guide = "• Try reinstalling: ./install.sh\n• Check Python installation"
            if self.is_termux:
                return base_guide + "\n• On Termux: pkg install python"
            elif self.is_macos:
                return base_guide + "\n• On macOS: Install Python via Homebrew or python.org"
            return base_guide
        
        # Command not found
        if "command not found" in error_msg:
            if self.is_termux:
                return "• Install with: pkg install <package-name>\n• Check if Termux packages are updated: pkg update"
            return "• Install required packages\n• Check if command is in PATH"
        
        return ""
    
    def _get_troubleshooting_guide(self) -> str:
        """Get general troubleshooting guide."""
        return (
            "\n\n[bold]🔧 Troubleshooting Steps:[/bold]\n"
            "1. Check if you have the latest version\n"
            "2. Verify your OpenRouter API key is set: neo setup\n"
            "3. Try reinstalling: ./install.sh\n"
            "4. Check GitHub issues: https://github.com/CVO-TreeAi/terminote\n"
            "\n[dim]Enable debug mode: export TERMINOTE_DEBUG=1[/dim]"
        )
    
    def _log_error(self, error: Exception, context: str):
        """Log error details for debugging."""
        log_dir = Path.home() / '.terminote' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'errors.log'
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Timestamp: {Path().absolute()}\n")
                f.write(f"Platform: {platform.platform()}\n")
                f.write(f"Termux: {self.is_termux}\n")
                f.write(f"Context: {context}\n")
                f.write(f"Error: {type(error).__name__}: {error}\n")
                f.write(f"Traceback:\n{traceback.format_exc()}\n")
        except Exception:
            # Don't let logging errors crash the application
            pass

def handle_with_context(context: str, user_message: str = None):
    """Decorator for adding error handling to functions."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            error_handler = ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, context, user_message)
                return None
        return wrapper
    return decorator

# Global error handler instance
error_handler = ErrorHandler()

def safe_execute(func: Callable, context: str = "", user_message: str = None, default_return=None):
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        error_handler.handle_error(e, context, user_message)
        return default_return 