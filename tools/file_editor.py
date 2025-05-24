"""
File editor utilities for TermiNote v5
Provides file editing and management capabilities.
"""

import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax
import tempfile
import subprocess

console = Console()

class FileEditor:
    """File editing utilities for TermiNote."""
    
    def __init__(self):
        self.editor = self._get_default_editor()
    
    def _get_default_editor(self) -> str:
        """Get the default text editor."""
        # Check environment variables
        for var in ['EDITOR', 'VISUAL']:
            if var in os.environ:
                return os.environ[var]
        
        # Check for common editors
        editors = ['code', 'subl', 'atom', 'vim', 'nano', 'emacs']
        for editor in editors:
            if self._command_exists(editor):
                return editor
        
        return 'nano'  # fallback
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def edit_file(self, file_path: str) -> bool:
        """Open a file in the default editor."""
        try:
            subprocess.run([self.editor, file_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error opening editor: {e}[/red]")
            return False
        except FileNotFoundError:
            console.print(f"[red]Editor '{self.editor}' not found[/red]")
            return False
    
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a new file with optional content."""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            console.print(f"[green]✅ File created: {file_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error creating file: {e}[/red]")
            return False
    
    def read_file(self, file_path: str) -> str:
        """Read and display file contents."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to detect file type for syntax highlighting
            file_ext = Path(file_path).suffix.lower()
            lexer_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.md': 'markdown',
                '.sh': 'bash',
                '.sql': 'sql'
            }
            
            lexer = lexer_map.get(file_ext, 'text')
            
            console.print(Panel(
                Syntax(content, lexer, theme="monokai", line_numbers=True),
                title=f"📄 {file_path}",
                border_style="blue"
            ))
            
            return content
            
        except FileNotFoundError:
            console.print(f"[red]File not found: {file_path}[/red]")
            return ""
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return ""
    
    def backup_file(self, file_path: str) -> str:
        """Create a backup of a file."""
        try:
            if not os.path.exists(file_path):
                console.print(f"[red]File not found: {file_path}[/red]")
                return ""
            
            backup_path = f"{file_path}.bak"
            counter = 1
            
            while os.path.exists(backup_path):
                backup_path = f"{file_path}.bak.{counter}"
                counter += 1
            
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            
            console.print(f"[green]✅ Backup created: {backup_path}[/green]")
            return backup_path
            
        except Exception as e:
            console.print(f"[red]Error creating backup: {e}[/red]")
            return ""
    
    def set_editor(self, editor: str):
        """Set the default editor."""
        if self._command_exists(editor):
            self.editor = editor
            console.print(f"[green]✅ Editor set to: {editor}[/green]")
        else:
            console.print(f"[red]Editor '{editor}' not found in PATH[/red]")
