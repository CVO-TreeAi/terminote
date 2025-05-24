"""
Session management for TermiNote v5
Handles creation, loading, and saving of writing sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .error_handler import SessionError, error_handler, safe_execute

console = Console()

class SessionManager:
    """Manages writing sessions for TermiNote."""
    
    def __init__(self):
        self.sessions_dir = Path.home() / '.terminote' / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_new_session(self, name: str = None) -> str:
        """Create a new writing session."""
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"session_{timestamp}"
        
        # Ensure unique name
        original_name = name
        counter = 1
        while self.session_exists(name):
            name = f"{original_name}_{counter}"
            counter += 1
        
        session_data = {
            'name': name,
            'created': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'content': '',
            'word_count': 0,
            'metadata': {
                'tags': [],
                'notes': '',
                'project': ''
            }
        }
        
        self.save_session(name, session_data)
        console.print(f"[green]✅ Created new session: {name}[/green]")
        return name
    
    def session_exists(self, name: str) -> bool:
        """Check if a session exists."""
        session_file = self.sessions_dir / f"{self._sanitize_name(name)}.json"
        return session_file.exists()
    
    def load_session(self, name: str) -> Dict:
        """Load a session by name."""
        session_file = self.sessions_dir / f"{self._sanitize_name(name)}.json"
        
        if not session_file.exists():
            console.print(f"[yellow]Session '{name}' not found. Creating new session.[/yellow]")
            return self._create_empty_session(name)
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Update last accessed
            session_data['last_accessed'] = datetime.now().isoformat()
            self.save_session(name, session_data)
            
            return session_data
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Use centralized error handling
            session_error = SessionError(f"Error loading session '{name}': {str(e)}")
            error_handler.handle_error(
                session_error,
                context="Session Loading",
                user_message=f"Could not load session '{name}'. Creating a new session instead."
            )
            return self._create_empty_session(name)
    
    def save_session(self, name: str, session_data: Dict) -> bool:
        """Save a session."""
        try:
            session_file = self.sessions_dir / f"{self._sanitize_name(name)}.json"
            
            # Update modification time
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Create backup if session already exists
            if session_file.exists():
                backup_file = session_file.with_suffix('.bak')
                session_file.rename(backup_file)
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            # Remove backup if save successful
            backup_file = session_file.with_suffix('.bak')
            if backup_file.exists():
                backup_file.unlink()
            
            return True
            
        except Exception as e:
            console.print(f"[red]Error saving session '{name}': {e}[/red]")
            
            # Restore backup if it exists
            backup_file = session_file.with_suffix('.bak')
            if backup_file.exists():
                backup_file.rename(session_file)
                console.print("[yellow]Restored from backup.[/yellow]")
            
            return False
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions with metadata."""
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    'name': session_data.get('name', session_file.stem),
                    'created': session_data.get('created', 'Unknown'),
                    'last_modified': session_data.get('last_modified', 'Unknown'),
                    'last_accessed': session_data.get('last_accessed', 'Never'),
                    'word_count': session_data.get('word_count', 0),
                    'has_content': bool(session_data.get('content', '').strip()),
                    'tags': session_data.get('metadata', {}).get('tags', []),
                    'project': session_data.get('metadata', {}).get('project', ''),
                    'file_path': str(session_file)
                })
                
            except (json.JSONDecodeError, KeyError) as e:
                console.print(f"[red]Error reading session {session_file.name}: {e}[/red]")
                continue
        
        # Sort by last modified (most recent first)
        sessions.sort(key=lambda x: x['last_modified'], reverse=True)
        
        # Display sessions table
        self._display_sessions_table(sessions)
        
        return sessions
    
    def _display_sessions_table(self, sessions: List[Dict]):
        """Display sessions in a formatted table."""
        if not sessions:
            console.print("[yellow]No sessions found.[/yellow]")
            return
        
        table = Table(title="Writing Sessions")
        table.add_column("Name", style="cyan")
        table.add_column("Words", justify="right", style="green")
        table.add_column("Last Modified", style="blue")
        table.add_column("Project", style="yellow")
        table.add_column("Tags", style="magenta")
        table.add_column("Status", style="white")
        
        for session in sessions:
            # Format dates
            try:
                last_mod = datetime.fromisoformat(session['last_modified'])
                formatted_date = last_mod.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = session['last_modified']
            
            # Status indicator
            status = "📝" if session['has_content'] else "📄"
            
            # Tags display
            tags_str = ", ".join(session['tags'][:3])  # Show first 3 tags
            if len(session['tags']) > 3:
                tags_str += "..."
            
            table.add_row(
                session['name'],
                str(session['word_count']),
                formatted_date,
                session['project'] or "-",
                tags_str or "-",
                status
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(sessions)} sessions in {self.sessions_dir}[/dim]")
    
    def delete_session(self, name: str) -> bool:
        """Delete a session."""
        session_file = self.sessions_dir / f"{self._sanitize_name(name)}.json"
        
        if not session_file.exists():
            console.print(f"[red]Session '{name}' not found.[/red]")
            return False
        
        try:
            # Create backup before deletion
            backup_file = session_file.with_suffix('.deleted')
            session_file.rename(backup_file)
            
            console.print(f"[green]✅ Session '{name}' deleted.[/green]")
            console.print(f"[dim]Backup saved as: {backup_file.name}[/dim]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error deleting session '{name}': {e}[/red]")
            return False
    
    def duplicate_session(self, source_name: str, new_name: str = None) -> Optional[str]:
        """Duplicate an existing session."""
        if not self.session_exists(source_name):
            console.print(f"[red]Source session '{source_name}' not found.[/red]")
            return None
        
        # Load source session
        source_session = self.load_session(source_name)
        
        # Generate new name if not provided
        if not new_name:
            new_name = f"{source_name}_copy"
        
        # Ensure unique name
        original_new_name = new_name
        counter = 1
        while self.session_exists(new_name):
            new_name = f"{original_new_name}_{counter}"
            counter += 1
        
        # Create new session data
        new_session = source_session.copy()
        new_session['name'] = new_name
        new_session['created'] = datetime.now().isoformat()
        new_session['last_modified'] = datetime.now().isoformat()
        new_session.pop('last_accessed', None)
        
        # Save new session
        if self.save_session(new_name, new_session):
            console.print(f"[green]✅ Session duplicated as: {new_name}[/green]")
            return new_name
        else:
            console.print("[red]Failed to duplicate session.[/red]")
            return None
    
    def export_session(self, name: str, export_path: str = None) -> bool:
        """Export session to a file."""
        if not self.session_exists(name):
            console.print(f"[red]Session '{name}' not found.[/red]")
            return False
        
        session = self.load_session(name)
        content = session.get('content', '')
        
        if not content.strip():
            console.print("[yellow]Session has no content to export.[/yellow]")
            return False
        
        if not export_path:
            # Generate default export path
            safe_name = self._sanitize_name(name)
            export_path = f"{safe_name}.md"
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                # Write header with metadata
                f.write(f"# {session.get('name', name)}\n\n")
                
                metadata = session.get('metadata', {})
                if metadata.get('project'):
                    f.write(f"**Project:** {metadata['project']}\n")
                if metadata.get('tags'):
                    f.write(f"**Tags:** {', '.join(metadata['tags'])}\n")
                if metadata.get('notes'):
                    f.write(f"**Notes:** {metadata['notes']}\n")
                
                f.write(f"**Created:** {session.get('created', 'Unknown')}\n")
                f.write(f"**Word Count:** {session.get('word_count', 0)}\n\n")
                f.write("---\n\n")
                
                # Write content
                f.write(content)
            
            console.print(f"[green]✅ Session exported to: {export_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error exporting session: {e}[/red]")
            return False
    
    def search_sessions(self, query: str) -> List[Dict]:
        """Search sessions by content or metadata."""
        query = query.lower()
        matching_sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Search in name, content, project, tags, and notes
                searchable_text = " ".join([
                    session_data.get('name', ''),
                    session_data.get('content', ''),
                    session_data.get('metadata', {}).get('project', ''),
                    session_data.get('metadata', {}).get('notes', ''),
                    " ".join(session_data.get('metadata', {}).get('tags', []))
                ]).lower()
                
                if query in searchable_text:
                    matching_sessions.append({
                        'name': session_data.get('name', session_file.stem),
                        'created': session_data.get('created', 'Unknown'),
                        'last_modified': session_data.get('last_modified', 'Unknown'),
                        'word_count': session_data.get('word_count', 0),
                        'project': session_data.get('metadata', {}).get('project', ''),
                        'tags': session_data.get('metadata', {}).get('tags', [])
                    })
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Display results
        if matching_sessions:
            console.print(Panel(
                f"[bold]Found {len(matching_sessions)} sessions matching '{query}'[/bold]",
                title="Search Results"
            ))
            self._display_sessions_table(matching_sessions)
        else:
            console.print(f"[yellow]No sessions found matching '{query}'[/yellow]")
        
        return matching_sessions
    
    def _create_empty_session(self, name: str) -> Dict:
        """Create an empty session data structure."""
        return {
            'name': name,
            'created': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'content': '',
            'word_count': 0,
            'metadata': {
                'tags': [],
                'notes': '',
                'project': ''
            }
        }
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize session name for use as filename."""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length and strip whitespace
        return name.strip()[:100]
    
    def get_session_stats(self) -> Dict:
        """Get statistics about all sessions."""
        sessions = []
        total_words = 0
        total_sessions = 0
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                sessions.append(session_data)
                total_words += session_data.get('word_count', 0)
                total_sessions += 1
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Calculate additional stats
        avg_words = total_words / total_sessions if total_sessions > 0 else 0
        sessions_with_content = len([s for s in sessions if s.get('content', '').strip()])
        
        stats = {
            'total_sessions': total_sessions,
            'sessions_with_content': sessions_with_content,
            'total_words': total_words,
            'average_words': round(avg_words, 1),
            'storage_path': str(self.sessions_dir)
        }
        
        # Display stats
        console.print(Panel(
            f"[bold]Session Statistics[/bold]\n\n"
            f"📊 Total Sessions: {stats['total_sessions']}\n"
            f"📝 With Content: {stats['sessions_with_content']}\n"
            f"📄 Empty: {stats['total_sessions'] - stats['sessions_with_content']}\n"
            f"🔤 Total Words: {stats['total_words']:,}\n"
            f"📈 Average Words: {stats['average_words']}\n\n"
            f"💾 Storage: {stats['storage_path']}",
            title="TermiNote Statistics"
        ))
        
        return stats
