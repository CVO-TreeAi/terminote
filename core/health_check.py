"""
Health check system for TermiNote v5
Validates that all components work correctly on the current platform.
"""

import os
import sys
import platform
import json
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .error_handler import error_handler, safe_execute
from .config_manager import ConfigManager
from .session import SessionManager
from .ai_client import OpenRouterClient

console = Console()

class HealthCheck:
    """Comprehensive health check for TermiNote across platforms."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.session_manager = SessionManager()
        self.ai_client = OpenRouterClient()
        self.is_termux = 'TERMUX_VERSION' in os.environ
        self.results = []
    
    def run_full_check(self) -> bool:
        """Run complete health check and return overall status."""
        console.print(Panel(
            "[bold]🩺 TermiNote Health Check[/bold]\n\n"
            f"Platform: {platform.platform()}\n"
            f"Termux: {'Yes' if self.is_termux else 'No'}",
            title="System Check"
        ))
        
        checks = [
            ("Python Environment", self._check_python),
            ("File Permissions", self._check_permissions),
            ("Configuration", self._check_config),
            ("Session Storage", self._check_sessions),
            ("Network Access", self._check_network),
            ("API Connection", self._check_api),
            ("Platform Features", self._check_platform_features)
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for check_name, check_func in checks:
                task = progress.add_task(f"Checking {check_name}...", total=1)
                
                result = safe_execute(
                    check_func,
                    context=f"Health Check: {check_name}",
                    default_return=(False, f"Failed to run {check_name} check")
                )
                
                if result:
                    status, message = result
                else:
                    status, message = False, f"Error in {check_name} check"
                
                self.results.append({
                    'check': check_name,
                    'status': status,
                    'message': message
                })
                
                progress.update(task, completed=1)
        
        self._display_results()
        return self._get_overall_status()
    
    def _check_python(self) -> Tuple[bool, str]:
        """Check Python environment."""
        issues = []
        
        # Python version
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            issues.append(f"Python version {version.major}.{version.minor} is too old (need 3.8+)")
        
        # Required modules
        required_modules = ['json', 'pathlib', 'rich', 'openai', 'yaml', 'click']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            issues.append(f"Missing modules: {', '.join(missing_modules)}")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, f"Python {version.major}.{version.minor}.{version.micro} with all required modules"
    
    def _check_permissions(self) -> Tuple[bool, str]:
        """Check file system permissions."""
        test_paths = [
            Path.home() / '.terminote',
            Path.home() / '.terminote' / 'sessions',
            Path.home() / '.terminote' / 'logs'
        ]
        
        for path in test_paths:
            try:
                # Try to create directory
                path.mkdir(parents=True, exist_ok=True)
                
                # Try to write a test file
                test_file = path / '.test_write'
                test_file.write_text("test")
                test_file.unlink()
                
            except PermissionError:
                guidance = ""
                if self.is_termux:
                    guidance = " (Try: termux-setup-storage)"
                return False, f"Cannot write to {path}{guidance}"
            except Exception as e:
                return False, f"Error accessing {path}: {str(e)}"
        
        return True, "All directories accessible and writable"
    
    def _check_config(self) -> Tuple[bool, str]:
        """Check configuration setup."""
        issues = []
        
        # Config file exists and is readable
        try:
            config_data = self.config.config
            if not config_data:
                issues.append("Config file is empty or invalid")
        except Exception as e:
            issues.append(f"Cannot read config: {str(e)}")
        
        # API key configuration
        api_key = self.config.get_api_key()
        if not api_key:
            issues.append("No OpenRouter API key configured")
        elif not api_key.startswith('sk-'):
            issues.append("API key format appears invalid")
        
        # Model configuration
        try:
            models = self.config.config.get('models', {})
            if not models.get('default'):
                issues.append("No default model configured")
        except Exception as e:
            issues.append(f"Model config error: {str(e)}")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Configuration is valid and complete"
    
    def _check_sessions(self) -> Tuple[bool, str]:
        """Check session management."""
        try:
            # Test session creation
            test_session = self.session_manager._create_empty_session("health_check_test")
            
            # Test session saving
            success = self.session_manager.save_session("health_check_test", test_session)
            if not success:
                return False, "Cannot save sessions"
            
            # Test session loading
            loaded = self.session_manager.load_session("health_check_test")
            if not loaded:
                return False, "Cannot load sessions"
            
            # Clean up
            self.session_manager.delete_session("health_check_test")
            
            return True, "Session management working correctly"
            
        except Exception as e:
            return False, f"Session error: {str(e)}"
    
    def _check_network(self) -> Tuple[bool, str]:
        """Check network connectivity."""
        import urllib.request
        import socket
        
        test_urls = [
            "https://openrouter.ai",
            "https://api.openrouter.ai",
            "https://www.google.com"
        ]
        
        working_urls = []
        failed_urls = []
        
        for url in test_urls:
            try:
                # Quick connectivity test with timeout
                urllib.request.urlopen(url, timeout=5)
                working_urls.append(url)
            except Exception:
                failed_urls.append(url)
        
        if not working_urls:
            guidance = ""
            if self.is_termux:
                guidance = " (Check Termux network permissions)"
            return False, f"No network connectivity{guidance}"
        
        if failed_urls:
            return True, f"Limited connectivity - {len(working_urls)}/{len(test_urls)} sites reachable"
        
        return True, "Full network connectivity"
    
    def _check_api(self) -> Tuple[bool, str]:
        """Check OpenRouter API connectivity."""
        if not self.config.get_api_key():
            return False, "No API key configured - run 'neo setup'"
        
        try:
            # Test API connection
            if self.ai_client.test_connection():
                return True, "API connection successful"
            else:
                return False, "API connection failed"
                
        except Exception as e:
            return False, f"API test error: {str(e)}"
    
    def _check_platform_features(self) -> Tuple[bool, str]:
        """Check platform-specific features."""
        features = []
        issues = []
        
        # Terminal capabilities
        try:
            import termios
            features.append("Terminal control")
        except ImportError:
            if not self.is_termux:  # Expected on some platforms
                issues.append("Limited terminal support")
        
        # Process management
        try:
            import subprocess
            subprocess.run(['echo', 'test'], capture_output=True, timeout=1)
            features.append("Process execution")
        except Exception:
            issues.append("Limited process support")
        
        # File watching (for auto-save)
        try:
            import watchdog
            features.append("File watching")
        except ImportError:
            # Not critical
            pass
        
        # Platform-specific checks
        if self.is_termux:
            # Check Termux-specific features
            termux_features = []
            
            # Storage access
            storage_path = Path.home() / 'storage'
            if storage_path.exists():
                termux_features.append("Storage access")
            
            # Package manager
            if Path('/data/data/com.termux/files/usr/bin/pkg').exists():
                termux_features.append("Package manager")
            
            features.extend(termux_features)
        
        status_msg = f"Platform features: {', '.join(features)}"
        if issues:
            status_msg += f" | Issues: {', '.join(issues)}"
            return len(features) > len(issues), status_msg
        
        return True, status_msg
    
    def _display_results(self):
        """Display health check results in a table."""
        table = Table(title="Health Check Results")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")
        
        for result in self.results:
            status_icon = "✅" if result['status'] else "❌"
            status_color = "green" if result['status'] else "red"
            
            table.add_row(
                result['check'],
                f"[{status_color}]{status_icon}[/{status_color}]",
                result['message']
            )
        
        console.print(table)
    
    def _get_overall_status(self) -> bool:
        """Get overall health status."""
        passed = sum(1 for r in self.results if r['status'])
        total = len(self.results)
        
        console.print(f"\n[bold]Overall Status: {passed}/{total} checks passed[/bold]")
        
        if passed == total:
            console.print("[green]✅ TermiNote is healthy and ready to use![/green]")
            return True
        elif passed >= total * 0.7:  # At least 70% passing
            console.print("[yellow]⚠️ TermiNote is mostly functional with some issues[/yellow]")
            return True
        else:
            console.print("[red]❌ TermiNote has significant issues that need attention[/red]")
            return False

def run_health_check() -> bool:
    """Run health check and return status."""
    checker = HealthCheck()
    return checker.run_full_check() 