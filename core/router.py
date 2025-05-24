"""
Main router for TermiNote v5
Handles navigation between different modes and manages user interactions.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import input_dialog, message_dialog

from .ai_client import OpenRouterClient
from .session import SessionManager
from .prompt_engine import PromptEngine

console = Console()

class Router:
    """Main router for handling different TermiNote modes."""
    
    def __init__(self):
        self.ai_client = OpenRouterClient()
        self.session_manager = SessionManager()
        self.prompt_engine = PromptEngine()
        self.prompt_session = PromptSession()
    
    def start_writing_session(self, session_name: str = None):
        """Start an interactive writing session."""
        if not session_name:
            session_name = self.session_manager.create_new_session()
        
        session = self.session_manager.load_session(session_name)
        
        console.print(Panel(
            f"[bold green]✍️  Writing Session: {session_name}[/bold green]\n\n"
            f"Words: {session.get('word_count', 0)} | "
            f"Last modified: {session.get('last_modified', 'Never')}\n\n"
            "[dim]Commands: /help, /save, /continue, /suggest, /chat, /quit[/dim]\n"
            "[yellow]Press Tab or /chat to toggle AI chat mode[/yellow]",
            title="Writing Mode"
        ))
        
        if session.get('content'):
            console.print("\n[dim]Current content:[/dim]")
            console.print(Markdown(session['content']))
            console.print("\n" + "─" * 50 + "\n")
        
        while True:
            try:
                user_input = self.prompt_session.prompt(
                    "📝 > ",
                    multiline=True,
                    wrap_lines=True
                )
                
                # Check for Tab key to toggle chat mode
                if user_input.strip() == "\t" or user_input.strip().startswith("/chat"):
                    self._toggle_chat_mode(session, session_name)
                    continue
                
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if self._handle_writing_command(user_input, session, session_name):
                        break
                    continue
                
                # Add content to session
                current_content = session.get('content', '')
                if current_content:
                    session['content'] = current_content + "\n\n" + user_input
                else:
                    session['content'] = user_input
                
                # Update word count
                session['word_count'] = len(session['content'].split())
                
                # Auto-save if enabled
                if self.ai_client.config.get_preference('auto_save'):
                    self.session_manager.save_session(session_name, session)
                
                console.print(f"[green]✅ Added {len(user_input.split())} words[/green]")
                
            except KeyboardInterrupt:
                if Confirm.ask("\nSave session before exiting?"):
                    self.session_manager.save_session(session_name, session)
                break
            except EOFError:
                break
    
    def _handle_writing_command(self, command: str, session: dict, session_name: str) -> bool:
        """Handle writing mode commands. Returns True if should exit."""
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower()
        
        if cmd == 'help':
            self._show_writing_help()
            
        elif cmd == 'save':
            self.session_manager.save_session(session_name, session)
            console.print("[green]✅ Session saved[/green]")
            
        elif cmd == 'continue':
            direction = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else ""
            self._continue_writing(session, direction)
            
        elif cmd == 'suggest':
            self._get_writing_suggestions(session)
        
        elif cmd == 'chat':
            self._toggle_chat_mode(session, session_name)
            
        elif cmd == 'outline':
            topic = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else None
            if not topic:
                topic = Prompt.ask("What topic would you like an outline for?")
            self._generate_outline(topic)
            
        elif cmd == 'brainstorm':
            topic = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else None
            if not topic:
                topic = Prompt.ask("What would you like to brainstorm about?")
            self._brainstorm_ideas(topic)
            
        elif cmd == 'export':
            self._export_session(session, session_name)
            
        elif cmd == 'quit' or cmd == 'exit':
            if Confirm.ask("Save session before exiting?"):
                self.session_manager.save_session(session_name, session)
            return True
            
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            self._show_writing_help()
        
        return False
    
    def _show_writing_help(self):
        """Show writing mode help."""
        help_text = """
[bold]Writing Mode Commands:[/bold]

[cyan]/help[/cyan]              - Show this help
[cyan]/save[/cyan]              - Save current session
[cyan]/chat[/cyan]              - Toggle AI chat mode (quick Q&A)
[cyan]/continue[/cyan] [direction] - AI continues your writing
[cyan]/suggest[/cyan]           - Get AI suggestions for improvement
[cyan]/outline[/cyan] [topic]   - Generate an outline
[cyan]/brainstorm[/cyan] [topic] - Brainstorm ideas
[cyan]/export[/cyan]            - Export session to file
[cyan]/quit[/cyan]              - Exit writing mode

[dim]Tip: Just start typing to add content to your document![/dim]
[yellow]Quick toggle: Press Tab or /chat to switch to AI chat mode[/yellow]
        """
        console.print(Panel(help_text, title="Help"))
    
    def _toggle_chat_mode(self, session: dict, session_name: str):
        """Toggle into AI chat mode while keeping document context."""
        console.print(Panel(
            f"[bold cyan]💬 AI Chat Mode[/bold cyan]\n\n"
            f"Document: {session_name} ({session.get('word_count', 0)} words)\n\n"
            "[dim]Chat with NEO about your document. Type '/back' to return to writing.[/dim]\n"
            "[yellow]NEO has full context of your current document[/yellow]",
            title="Chat Mode"
        ))
        
        document_context = f"Current document '{session_name}':\n{session.get('content', 'No content yet.')}"
        
        while True:
            try:
                chat_input = self.prompt_session.prompt("💬 Ask NEO > ")
                
                if not chat_input.strip():
                    continue
                    
                # Exit chat mode
                if chat_input.strip().lower() in ['/back', '/write', '/exit', '/return']:
                    console.print("[green]🔙 Returning to writing mode...[/green]")
                    break
                
                # Special chat commands
                if chat_input.startswith('/'):
                    if self._handle_chat_command(chat_input, session, session_name):
                        break
                    continue
                
                # Send query to AI with document context
                console.print("[cyan]🤖 NEO is thinking...[/cyan]")
                
                messages = [
                    {
                        "role": "system",
                        "content": f"""You are NEO, an AI writing assistant. The user is working on a document and has switched to chat mode to ask you questions or get help. 

DOCUMENT CONTEXT:
{document_context}

Provide helpful, concise responses about their writing, offer suggestions, answer questions, or help them brainstorm. Keep responses focused and actionable."""
                    },
                    {
                        "role": "user",
                        "content": chat_input
                    }
                ]
                
                response_text = ""
                with Live(console=console, refresh_per_second=4) as live:
                    for chunk in self.ai_client.chat_completion(messages, task='writing'):
                        response_text += chunk
                        live.update(Panel(
                            Markdown(response_text),
                            title="💬 NEO Response"
                        ))
                
                console.print("")  # Add spacing
                
            except KeyboardInterrupt:
                console.print("\n[green]🔙 Returning to writing mode...[/green]")
                break
            except EOFError:
                break
    
    def _handle_chat_command(self, command: str, session: dict, session_name: str) -> bool:
        """Handle chat mode commands. Returns True if should exit chat."""
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower()
        
        if cmd == 'help':
            self._show_chat_help()
        elif cmd == 'continue':
            direction = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else ""
            self._continue_writing(session, direction)
        elif cmd == 'suggest':
            self._get_writing_suggestions(session)
        elif cmd == 'back' or cmd == 'write' or cmd == 'return':
            return True
        else:
            console.print(f"[red]Unknown chat command: {cmd}[/red]")
            self._show_chat_help()
        
        return False
    
    def _show_chat_help(self):
        """Show chat mode help."""
        help_text = """
[bold]Chat Mode Commands:[/bold]

[cyan]/back[/cyan]              - Return to writing mode
[cyan]/continue[/cyan] [direction] - AI continues your writing
[cyan]/suggest[/cyan]           - Get AI suggestions for improvement
[cyan]/help[/cyan]              - Show this help

[dim]Just type naturally to chat with NEO about your document![/dim]
        """
        console.print(Panel(help_text, title="Chat Help"))
    
    def _continue_writing(self, session: dict, direction: str = ""):
        """Use AI to continue writing."""
        content = session.get('content', '')
        if not content:
            console.print("[yellow]No content to continue from. Start writing first![/yellow]")
            return
        
        console.print("[cyan]🤖 AI is continuing your writing...[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.continue_writing(content, direction):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title="AI Continuation"
                ))
        
        if Confirm.ask("\nAdd this continuation to your document?"):
            session['content'] = content + "\n\n" + response_text
            session['word_count'] = len(session['content'].split())
            console.print("[green]✅ AI continuation added[/green]")
    
    def _get_writing_suggestions(self, session: dict):
        """Get AI suggestions for improving writing."""
        content = session.get('content', '')
        if not content:
            console.print("[yellow]No content to review. Write something first![/yellow]")
            return
        
        console.print("[cyan]🤖 AI is reviewing your writing...[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.get_writing_suggestions(content):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title="Writing Suggestions"
                ))
    
    def _generate_outline(self, topic: str):
        """Generate an outline for a topic."""
        console.print(f"[cyan]🤖 Generating outline for: {topic}[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.generate_outline(topic):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title=f"Outline: {topic}"
                ))
    
    def _brainstorm_ideas(self, topic: str):
        """Brainstorm ideas on a topic."""
        console.print(f"[cyan]🤖 Brainstorming ideas for: {topic}[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.brainstorm_ideas(topic):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title=f"Ideas: {topic}"
                ))
    
    def _export_session(self, session: dict, session_name: str):
        """Export session to a file."""
        content = session.get('content', '')
        if not content:
            console.print("[yellow]No content to export![/yellow]")
            return
        
        # Default filename
        safe_name = "".join(c for c in session_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        default_filename = f"{safe_name}.md"
        
        filename = Prompt.ask("Export filename", default=default_filename)
        
        try:
            with open(filename, 'w') as f:
                f.write(f"# {session_name}\n\n")
                f.write(content)
            
            console.print(f"[green]✅ Exported to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/red]")
    
    def start_project_session(self, project_name: str = None):
        """Start a project planning session."""
        if not project_name:
            project_name = Prompt.ask("Project name")
        
        console.print(Panel(
            f"[bold yellow]🏗️  Project: {project_name}[/bold yellow]\n\n"
            "[dim]Commands: /plan, /tasks, /docs, /code-review, /help, /quit[/dim]",
            title="Project Mode"
        ))
        
        while True:
            try:
                user_input = self.prompt_session.prompt("🏗️  > ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if self._handle_project_command(user_input, project_name):
                        break
                    continue
                
                # Default: treat as project question
                self._ask_project_question(user_input, project_name)
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    def _handle_project_command(self, command: str, project_name: str) -> bool:
        """Handle project mode commands. Returns True if should exit."""
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower()
        
        if cmd == 'help':
            self._show_project_help()
            
        elif cmd == 'plan':
            description = ' '.join(cmd_parts[1:]) if len(cmd_parts) > 1 else project_name
            self._generate_project_plan(description)
            
        elif cmd == 'tasks':
            self._generate_task_breakdown(project_name)
            
        elif cmd == 'docs':
            doc_type = cmd_parts[1] if len(cmd_parts) > 1 else 'readme'
            self._generate_documentation(project_name, doc_type)
            
        elif cmd == 'code-review' or cmd == 'review':
            self._interactive_code_review()
            
        elif cmd == 'quit' or cmd == 'exit':
            return True
            
        else:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            self._show_project_help()
        
        return False
    
    def _show_project_help(self):
        """Show project mode help."""
        help_text = """
[bold]Project Mode Commands:[/bold]

[cyan]/help[/cyan]                    - Show this help
[cyan]/plan[/cyan] [description]      - Generate project development plan
[cyan]/tasks[/cyan]                   - Break down project into tasks
[cyan]/docs[/cyan] [type]            - Generate documentation (readme, api-docs, etc.)
[cyan]/code-review[/cyan]             - Interactive code review
[cyan]/quit[/cyan]                    - Exit project mode

[dim]Or just ask questions about your project![/dim]
        """
        console.print(Panel(help_text, title="Help"))
    
    def _generate_project_plan(self, description: str):
        """Generate a project development plan."""
        console.print(f"[cyan]🤖 Creating development plan for: {description}[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.develop_project_plan(description):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title="Project Development Plan"
                ))
    
    def _generate_task_breakdown(self, project_name: str):
        """Generate task breakdown for project."""
        # This could be enhanced with more specific prompts
        self._ask_project_question(f"Break down {project_name} into specific development tasks with priorities", project_name)
    
    def _generate_documentation(self, project_name: str, doc_type: str):
        """Generate project documentation."""
        prompt = f"Generate {doc_type} documentation for the {project_name} project"
        self._ask_project_question(prompt, project_name)
    
    def _interactive_code_review(self):
        """Interactive code review session."""
        console.print("[cyan]📋 Paste your code for review (Ctrl+D when done):[/cyan]")
        
        code_lines = []
        try:
            while True:
                line = input()
                code_lines.append(line)
        except EOFError:
            pass
        
        if not code_lines:
            console.print("[yellow]No code provided for review[/yellow]")
            return
        
        code = '\n'.join(code_lines)
        language = Prompt.ask("Programming language", default="python")
        
        console.print(f"[cyan]🤖 Reviewing {language} code...[/cyan]")
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.review_code(code, language):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title="Code Review"
                ))
    
    def _ask_project_question(self, question: str, project_context: str):
        """Ask a general project question."""
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert software architect and project manager helping with the "{project_context}" project. 
                Provide detailed, practical advice and solutions. Focus on:
                - Technical feasibility and best practices
                - Clear implementation steps
                - Potential challenges and solutions
                - Resource and timeline considerations"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        response_text = ""
        with Live(console=console, refresh_per_second=4) as live:
            for chunk in self.ai_client.chat_completion(messages, task='coding'):
                response_text += chunk
                live.update(Panel(
                    Markdown(response_text),
                    title="Project Assistant"
                ))
