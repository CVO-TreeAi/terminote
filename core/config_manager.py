"""
Configuration management for TermiNote v5
Handles API keys, model selection, and user preferences.
"""

import json
import os
import yaml
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv, set_key
from .error_handler import ConfigurationError, error_handler

console = Console()

class ConfigManager:
    """Manages TermiNote configuration including API keys and model preferences."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.terminote'
        self.config_file = self.config_dir / 'config.yaml'
        self.env_file = self.config_dir / '.env'
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv(self.env_file)
        
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        else:
            return self._default_config()
    
    def _default_config(self):
        """Return default configuration."""
        return {
            'models': {
                'default': 'anthropic/claude-3.5-sonnet',
                'writing': 'anthropic/claude-3.5-sonnet',
                'coding': 'anthropic/claude-3.5-sonnet',
                'quick': 'anthropic/claude-3-haiku'
            },
            'preferences': {
                'auto_save': True,
                'session_backup': True,
                'max_tokens': 4096,
                'temperature': 0.7
            },
            'ui': {
                'theme': 'dark',
                'show_token_count': True,
                'auto_format': True
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def interactive_setup(self):
        """Interactive setup wizard for first-time configuration."""
        console.print("\n[bold blue]Welcome to TermiNote v5 Setup![/bold blue]\n")
        
        # API Key setup
        self._setup_api_key()
        
        # Model selection
        self._setup_models()
        
        # Preferences
        self._setup_preferences()
        
        # Save configuration
        self.save_config()
        
        console.print("\n[bold green]✅ Setup complete! You're ready to use TermiNote.[/bold green]")
        console.print("Run [bold cyan]`terminote write`[/bold cyan] to start your first writing session.")
    
    def _setup_api_key(self):
        """Setup OpenRouter API key."""
        console.print(Panel(
            "[bold]OpenRouter API Configuration[/bold]\n\n"
            "You'll need an OpenRouter API key to use TermiNote.\n"
            "Get one at: https://openrouter.ai/keys",
            title="🔑 API Setup"
        ))
        
        current_key = os.getenv('OPENROUTER_API_KEY', '')
        if current_key:
            console.print(f"[green]Current API key: {current_key[:8]}...{current_key[-4:]}[/green]")
            if not Confirm.ask("Would you like to update your API key?"):
                return
        
        api_key = Prompt.ask(
            "Enter your OpenRouter API key",
            password=True,
            default=current_key if current_key else None
        )
        
        if api_key:
            # Save to .env file
            set_key(str(self.env_file), 'OPENROUTER_API_KEY', api_key)
            console.print("[green]✅ API key saved securely.[/green]")
        else:
            console.print("[yellow]⚠️  No API key provided. You can set it later.[/yellow]")
    
    def _setup_models(self):
        """Setup model preferences."""
        console.print(Panel(
            "[bold]Model Configuration[/bold]\n\n"
            "Choose your preferred models for different tasks:",
            title="🤖 Model Setup"
        ))
        
        available_models = [
            'anthropic/claude-3.5-sonnet',
            'anthropic/claude-3-opus',
            'anthropic/claude-3-haiku',
            'openai/gpt-4o',
            'openai/gpt-4o-mini',
            'meta-llama/llama-3.1-8b-instruct',
            'google/gemini-pro-1.5',
            'mistralai/mistral-large'
        ]
        
        # Show current models
        table = Table(title="Current Model Configuration")
        table.add_column("Task", style="cyan")
        table.add_column("Model", style="green")
        
        for task, model in self.config['models'].items():
            table.add_row(task.capitalize(), model)
        
        console.print(table)
        
        if Confirm.ask("\nWould you like to customize model selection?"):
            for task in ['writing', 'coding', 'quick']:
                console.print(f"\n[bold]Available models for {task}:[/bold]")
                for i, model in enumerate(available_models, 1):
                    console.print(f"  {i}. {model}")
                
                choice = Prompt.ask(
                    f"Select model for {task} (1-{len(available_models)} or current: {self.config['models'][task]})",
                    default=str(available_models.index(self.config['models'][task]) + 1)
                )
                
                try:
                    model_index = int(choice) - 1
                    if 0 <= model_index < len(available_models):
                        self.config['models'][task] = available_models[model_index]
                        console.print(f"[green]✅ {task} model set to {available_models[model_index]}[/green]")
                except ValueError:
                    console.print("[yellow]Invalid selection, keeping current model.[/yellow]")
    
    def _setup_preferences(self):
        """Setup user preferences."""
        console.print(Panel(
            "[bold]Preferences[/bold]\n\n"
            "Configure your TermiNote experience:",
            title="⚙️  Preferences"
        ))
        
        # Temperature setting
        current_temp = self.config['preferences']['temperature']
        temp = Prompt.ask(
            f"Model temperature (creativity level, 0.0-1.0)",
            default=str(current_temp)
        )
        try:
            self.config['preferences']['temperature'] = float(temp)
        except ValueError:
            console.print("[yellow]Invalid temperature, keeping current setting.[/yellow]")
        
        # Max tokens
        current_tokens = self.config['preferences']['max_tokens']
        tokens = Prompt.ask(
            f"Maximum tokens per response",
            default=str(current_tokens)
        )
        try:
            self.config['preferences']['max_tokens'] = int(tokens)
        except ValueError:
            console.print("[yellow]Invalid token count, keeping current setting.[/yellow]")
        
        # Auto-save
        self.config['preferences']['auto_save'] = Confirm.ask(
            "Enable auto-save for sessions?",
            default=self.config['preferences']['auto_save']
        )
    
    def show_config(self):
        """Display current configuration."""
        console.print(Panel(
            "[bold]TermiNote Configuration[/bold]",
            title="⚙️  Current Settings"
        ))
        
        # API Key status
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        if api_key:
            console.print(f"[green]🔑 API Key: {api_key[:8]}...{api_key[-4:]}[/green]")
        else:
            console.print("[red]🔑 API Key: Not configured[/red]")
        
        # Models table
        models_table = Table(title="Models")
        models_table.add_column("Task", style="cyan")
        models_table.add_column("Model", style="green")
        
        for task, model in self.config['models'].items():
            models_table.add_row(task.capitalize(), model)
        
        console.print(models_table)
        
        # Preferences table
        prefs_table = Table(title="Preferences")
        prefs_table.add_column("Setting", style="cyan")
        prefs_table.add_column("Value", style="green")
        
        for setting, value in self.config['preferences'].items():
            prefs_table.add_row(setting.replace('_', ' ').title(), str(value))
        
        console.print(prefs_table)
        
        console.print(f"\n[dim]Config file: {self.config_file}[/dim]")
    
    def get_api_key(self):
        """Get the OpenRouter API key."""
        return os.getenv('OPENROUTER_API_KEY', '')
    
    def get_model(self, task='default'):
        """Get model for specific task."""
        return self.config['models'].get(task, self.config['models']['default'])
    
    def get_preference(self, key):
        """Get a specific preference value."""
        return self.config['preferences'].get(key) 