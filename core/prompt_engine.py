"""
Prompt engine for TermiNote v5
Manages and optimizes prompts for different AI tasks.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console

console = Console()

class PromptEngine:
    """Manages prompts and templates for AI interactions."""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.user_prompts_dir = Path.home() / '.terminote' / 'prompts'
        self.user_prompts_dir.mkdir(parents=True, exist_ok=True)
        
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict:
        """Load prompts from files."""
        prompts = {}
        
        # Load default prompts
        for prompt_file in self.prompts_dir.glob("*.md"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                prompts[prompt_file.stem] = content
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load prompt {prompt_file.name}: {e}[/yellow]")
        
        # Load user prompts (override defaults)
        for prompt_file in self.user_prompts_dir.glob("*.md"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                prompts[prompt_file.stem] = content
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load user prompt {prompt_file.name}: {e}[/yellow]")
        
        return prompts
    
    def get_prompt(self, prompt_name: str, variables: Dict = None) -> str:
        """Get a prompt by name with variable substitution."""
        if prompt_name not in self.prompts:
            console.print(f"[yellow]Warning: Prompt '{prompt_name}' not found[/yellow]")
            return f"You are a helpful AI assistant for {prompt_name} tasks."
        
        prompt = self.prompts[prompt_name]
        
        # Substitute variables if provided
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def list_prompts(self) -> List[str]:
        """List available prompts."""
        return list(self.prompts.keys())
    
    def reload_prompts(self):
        """Reload prompts from files."""
        self.prompts = self._load_prompts()
        console.print("[green]✅ Prompts reloaded[/green]")
