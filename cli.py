#!/usr/bin/env python3
"""
TermiNote v5 - AI-native CLI for focused writing, dev planning, and document generation.
"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.router import Router
from core.session import SessionManager
from core.prompt_engine import PromptEngine
from core.health_check import run_health_check
from tools.docbuilder import DocBuilder
from tools.file_editor import FileEditor

console = Console()

@click.group()
@click.version_option(version="5.0.0", prog_name="TermiNote")
def cli():
    """TermiNote v5 - AI-native CLI for focused writing and development planning."""
    pass

@cli.command()
def setup():
    """Initial setup: configure API keys and preferences."""
    console.print(Panel(
        Text("🚀 TermiNote v5 Setup", style="bold blue"),
        subtitle="Configure your AI writing assistant"
    ))
    
    from core.config_manager import ConfigManager
    config = ConfigManager()
    config.interactive_setup()

@cli.command()
@click.option('--session', '-s', help='Session name (optional)')
def write(session):
    """Start an interactive writing session."""
    console.print(Panel(
        Text("✍️  Writing Mode", style="bold green"),
        subtitle="AI-powered focused writing"
    ))
    
    session_mgr = SessionManager()
    session_name = session or session_mgr.create_new_session()
    
    router = Router()
    router.start_writing_session(session_name)

@cli.command()
@click.option('--name', '-n', help='Project name')
def project(name):
    """Create or continue working on a project."""
    console.print(Panel(
        Text("🏗️  Project Mode", style="bold yellow"),
        subtitle="Development planning and documentation"
    ))
    
    router = Router()
    router.start_project_session(name)

@cli.command()
@click.argument('document_type', type=click.Choice(['readme', 'spec', 'api-docs', 'guide']))
@click.option('--output', '-o', help='Output file path')
def generate(document_type, output):
    """Generate documentation using AI."""
    console.print(Panel(
        Text(f"📝 Generating {document_type.upper()}", style="bold magenta"),
        subtitle="AI document generation"
    ))
    
    builder = DocBuilder()
    builder.generate_document(document_type, output)

@cli.command()
def sessions():
    """List and manage writing sessions."""
    session_mgr = SessionManager()
    session_mgr.list_sessions()

@cli.command()
def config():
    """View and edit configuration."""
    from core.config_manager import ConfigManager
    config = ConfigManager()
    config.show_config()

@cli.command()
def doctor():
    """Run system health check and diagnostics."""
    console.print(Panel(
        Text("🩺 Health Check", style="bold cyan"),
        subtitle="System diagnostics and troubleshooting"
    ))
    
    success = run_health_check()
    if not success:
        console.print("\n[yellow]Some issues detected. Run 'neo setup' if needed.[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    cli() 