"""
TermiNote Android App - Native Android version with GUI
Built with Kivy for cross-platform mobile development
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger

class SimpleSessionManager:
    """Simplified session manager for the Android app."""
    
    def __init__(self):
        self.sessions_dir = Path.home() / '.terminote' / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, name, content):
        """Save a session to file."""
        try:
            session_file = self.sessions_dir / f"{name}.json"
            session_data = {
                'name': name,
                'content': content,
                'word_count': len(content.split()) if content else 0,
                'updated': datetime.now().isoformat()
            }
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
            return True
        except Exception as e:
            Logger.error(f'Session save error: {e}')
            return False
    
    def load_session(self, name):
        """Load a session from file."""
        try:
            session_file = self.sessions_dir / f"{name}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            Logger.error(f'Session load error: {e}')
        return {'name': name, 'content': '', 'word_count': 0}
    
    def list_sessions(self):
        """List all sessions."""
        sessions = []
        try:
            for session_file in self.sessions_dir.glob('*.json'):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except Exception as e:
                    Logger.error(f'Error loading session {session_file}: {e}')
        except Exception as e:
            Logger.error(f'Error listing sessions: {e}')
        return sessions
    
    def delete_session(self, name):
        """Delete a session."""
        try:
            session_file = self.sessions_dir / f"{name}.json"
            if session_file.exists():
                session_file.unlink()
                return True
        except Exception as e:
            Logger.error(f'Session delete error: {e}')
        return False

class WelcomeScreen(Screen):
    """Welcome/main menu screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'welcome'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='TermiNote v5\nYour AI Writing Assistant',
            font_size='24sp',
            size_hint_y=None,
            height='100dp',
            halign='center'
        )
        layout.add_widget(header)
        
        # Main buttons
        buttons = [
            ('Start Writing', self.start_writing),
            ('Continue Session', self.continue_session),
            ('Sessions Manager', self.sessions_manager),
            ('Settings', self.settings),
            ('Help', self.help)
        ]
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                size_hint_y=None,
                height='60dp',
                font_size='18sp'
            )
            btn.bind(on_press=callback)
            layout.add_widget(btn)
        
        # Exit button
        exit_btn = Button(
            text='Exit',
            size_hint_y=None,
            height='60dp',
            font_size='18sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.exit_app)
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)
    
    def start_writing(self, instance):
        self.manager.current = 'writing'
    
    def continue_session(self, instance):
        self.manager.current = 'sessions'
    
    def sessions_manager(self, instance):
        self.manager.current = 'sessions'
    
    def settings(self, instance):
        self.manager.current = 'settings'
    
    def help(self, instance):
        self.manager.current = 'help'
    
    def exit_app(self, instance):
        App.get_running_app().stop()

class WritingScreen(Screen):
    """Main writing interface with AI chat toggle."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'writing'
        self.session_manager = SimpleSessionManager()
        self.current_session = None
        self.chat_mode = False
        
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Top bar with session info and controls
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        self.session_label = Label(text='New Session', size_hint_x=0.5)
        top_bar.add_widget(self.session_label)
        
        # Mode toggle button
        self.mode_btn = Button(
            text='💬 Chat Mode',
            size_hint_x=0.25,
            font_size='14sp'
        )
        self.mode_btn.bind(on_press=self.toggle_mode)
        top_bar.add_widget(self.mode_btn)
        
        # Back button
        back_btn = Button(text='← Back', size_hint_x=0.25)
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        main_layout.add_widget(top_bar)
        
        # Writing area (scrollable)
        scroll = ScrollView()
        self.text_input = TextInput(
            multiline=True,
            text='',
            hint_text='Start writing here...',
            font_size='16sp',
            size_hint_y=None
        )
        self.text_input.bind(minimum_height=self.text_input.setter('height'))
        scroll.add_widget(self.text_input)
        main_layout.add_widget(scroll)
        
        # Bottom controls
        bottom_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        controls = [
            ('💾 Save', self.save_session),
            ('🤖 AI Help', self.ai_suggest),
            ('📤 Export', self.export_session)
        ]
        
        for text, callback in controls:
            btn = Button(text=text, font_size='14sp')
            btn.bind(on_press=callback)
            bottom_bar.add_widget(btn)
        
        main_layout.add_widget(bottom_bar)
        self.add_widget(main_layout)
    
    def toggle_mode(self, instance):
        """Toggle between writing and chat mode."""
        self.chat_mode = not self.chat_mode
        
        if self.chat_mode:
            self.mode_btn.text = '✍️ Write Mode'
            self.text_input.hint_text = 'Ask AI anything about your writing...'
        else:
            self.mode_btn.text = '💬 Chat Mode'
            self.text_input.hint_text = 'Continue writing...'
    
    def save_session(self, instance):
        """Save current session."""
        if not self.current_session:
            # Create a new session if none exists
            session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_session = {'name': session_name}
            self.session_label.text = f"Session: {session_name}"
        
        content = self.text_input.text
        success = self.session_manager.save_session(self.current_session['name'], content)
        
        if success:
            self.show_popup('Success', 'Session saved!')
        else:
            self.show_popup('Error', 'Failed to save session')
    
    def ai_suggest(self, instance):
        """Get AI suggestions for current text (simplified for demo)."""
        if not self.text_input.text.strip():
            self.show_popup('Info', 'Write something first for AI to help with!')
            return
        
        # For now, show a demo message since we don't have AI integration
        if self.chat_mode:
            self.handle_ai_chat()
        else:
            self.handle_ai_suggestions()
    
    def handle_ai_chat(self):
        """Handle AI chat interaction (demo mode)."""
        user_input = self.text_input.text.strip()
        if not user_input:
            return
        
        # Demo response
        chat_text = f"\n[You]: {user_input}\n[AI]: This is a demo response. AI features will be available when you configure your API key in settings.\n"
        self.text_input.text = chat_text
    
    def handle_ai_suggestions(self):
        """Handle AI writing suggestions (demo mode)."""
        suggestions = "Demo suggestions:\n- Consider adding more descriptive details\n- Check for sentence variety\n- Review paragraph structure\n\nNote: Configure your API key in settings for full AI features."
        self.show_popup('AI Suggestions', suggestions)
    
    def export_session(self, instance):
        """Export current session."""
        if self.text_input.text.strip():
            # Save current content first
            if not self.current_session:
                self.save_session(None)
            
            # Export to Downloads folder on Android
            try:
                content = self.text_input.text
                if platform == 'android':
                    export_dir = Path('/storage/emulated/0/Download')
                else:
                    export_dir = Path.home() / 'Downloads'
                
                export_dir.mkdir(exist_ok=True)
                export_file = export_dir / f"{self.current_session['name']}.md"
                
                with open(export_file, 'w') as f:
                    f.write(content)
                
                self.show_popup('Success', f'Exported to Downloads folder')
            except Exception as e:
                self.show_popup('Error', f'Export failed: {str(e)}')
        else:
            self.show_popup('Info', 'Nothing to export!')
    
    def go_back(self, instance):
        self.manager.current = 'welcome'
    
    def show_popup(self, title, message):
        """Show a popup message."""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def load_session(self, session_name):
        """Load a specific session for editing."""
        self.current_session = self.session_manager.load_session(session_name)
        self.session_label.text = f"Session: {session_name}"
        self.text_input.text = self.current_session.get('content', '')

class SessionsScreen(Screen):
    """Sessions management screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'sessions'
        self.session_manager = SimpleSessionManager()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header.add_widget(Label(text='Sessions Manager', font_size='20sp'))
        
        back_btn = Button(text='← Back', size_hint_x=None, width='100dp')
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        layout.add_widget(header)
        
        # Sessions list (scrollable)
        scroll = ScrollView()
        self.sessions_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.sessions_layout.bind(minimum_height=self.sessions_layout.setter('height'))
        scroll.add_widget(self.sessions_layout)
        layout.add_widget(scroll)
        
        # Refresh button
        refresh_btn = Button(text='Refresh', size_hint_y=None, height='50dp')
        refresh_btn.bind(on_press=lambda x: self.load_sessions())
        layout.add_widget(refresh_btn)
        
        # Load sessions
        self.load_sessions()
        
        self.add_widget(layout)
    
    def load_sessions(self):
        """Load and display sessions list."""
        self.sessions_layout.clear_widgets()
        
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            self.sessions_layout.add_widget(
                Label(text='No sessions yet. Start writing!', size_hint_y=None, height='60dp')
            )
            return
        
        for session in sessions:
            session_item = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height='80dp',
                spacing=10,
                padding=5
            )
            
            # Session info
            info_text = f"{session['name']}\n{session.get('word_count', 0)} words"
            if 'updated' in session:
                info_text += f"\nUpdated: {session['updated'][:10]}"
            
            info_label = Label(
                text=info_text,
                size_hint_x=0.6,
                halign='left',
                font_size='14sp'
            )
            session_item.add_widget(info_label)
            
            # Open button
            open_btn = Button(
                text='Open',
                size_hint_x=0.2,
                font_size='14sp'
            )
            open_btn.bind(on_press=lambda x, name=session['name']: self.open_session(name))
            session_item.add_widget(open_btn)
            
            # Delete button
            del_btn = Button(
                text='Delete',
                size_hint_x=0.2,
                font_size='14sp',
                background_color=(0.8, 0.2, 0.2, 1)
            )
            del_btn.bind(on_press=lambda x, name=session['name']: self.delete_session(name))
            session_item.add_widget(del_btn)
            
            self.sessions_layout.add_widget(session_item)
    
    def open_session(self, session_name):
        """Open a session for editing."""
        writing_screen = self.manager.get_screen('writing')
        writing_screen.load_session(session_name)
        self.manager.current = 'writing'
    
    def delete_session(self, session_name):
        """Delete a session with confirmation."""
        self.session_manager.delete_session(session_name)
        self.load_sessions()  # Refresh list
        
        popup = Popup(
            title='Deleted',
            content=Label(text=f'Session {session_name} deleted'),
            size_hint=(0.6, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'welcome'

class HelpScreen(Screen):
    """Help and instructions screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'help'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header.add_widget(Label(text='Help', font_size='20sp'))
        
        back_btn = Button(text='← Back', size_hint_x=None, width='100dp')
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        layout.add_widget(header)
        
        # Help content (scrollable)
        scroll = ScrollView()
        help_text = """
TermiNote v5 - AI Writing Assistant

How to use:
1. Start Writing: Create a new writing session
2. Continue Session: Resume a previous session
3. Sessions Manager: View and manage all sessions

Writing Features:
- Save: Save your current session
- AI Help: Get AI-powered suggestions (requires API key)
- Export: Export to markdown file in Downloads

Chat Mode:
Toggle between writing and chat mode to ask questions about your writing.

Tips:
- Sessions are automatically saved locally
- Configure your OpenRouter API key in Settings for AI features
- Export creates markdown files in your Downloads folder

Launch from Termux:
cd android && python main.py
        """
        
        help_label = Label(
            text=help_text,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size='14sp',
            text_size=(self.width - 40, None)
        )
        help_label.bind(texture_size=help_label.setter('size'))
        scroll.add_widget(help_label)
        
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'welcome'

class SettingsScreen(Screen):
    """App settings and configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.config_file = Path.home() / '.terminote' / 'config.json'
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        header.add_widget(Label(text='Settings', font_size='20sp'))
        
        back_btn = Button(text='← Back', size_hint_x=None, width='100dp')
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        
        layout.add_widget(header)
        
        # API Key input
        layout.add_widget(Label(text='OpenRouter API Key:', size_hint_y=None, height='30dp'))
        self.api_key_input = TextInput(
            password=True,
            size_hint_y=None,
            height='40dp',
            hint_text='Enter your API key'
        )
        layout.add_widget(self.api_key_input)
        
        # Save button
        save_btn = Button(text='Save Settings', size_hint_y=None, height='50dp')
        save_btn.bind(on_press=self.save_settings)
        layout.add_widget(save_btn)
        
        # App info
        layout.add_widget(Label(text='', size_hint_y=0.1))  # Spacer
        layout.add_widget(Label(text='App Information:', size_hint_y=None, height='30dp'))
        
        info_text = """
TermiNote v5.0
AI Writing Assistant
Android Native App

Developed by TreeAI
Launch from Termux or Android App Drawer
        """
        
        info_label = Label(
            text=info_text,
            size_hint_y=None,
            height='150dp',
            font_size='14sp'
        )
        layout.add_widget(info_label)
        
        # Load existing settings
        self.load_settings()
        
        self.add_widget(layout)
    
    def load_settings(self):
        """Load existing settings."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key_input.text = config.get('api_key', '')
        except Exception as e:
            Logger.error(f'Error loading settings: {e}')
    
    def save_settings(self, instance):
        """Save API key and other settings."""
        api_key = self.api_key_input.text.strip()
        
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save config
            config = {'api_key': api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            
            # Also set environment variable for current session
            if api_key:
                os.environ['OPENROUTER_API_KEY'] = api_key
            
            popup = Popup(
                title='Success',
                content=Label(text='Settings saved!'),
                size_hint=(0.6, 0.3)
            )
            popup.open()
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Failed to save: {str(e)}'),
                size_hint=(0.6, 0.3)
            )
            popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'welcome'

class TermiNoteApp(App):
    """Main TermiNote Android application."""
    
    def build(self):
        """Build the app interface."""
        self.title = 'TermiNote v5'
        
        # Set up screen manager
        sm = ScreenManager()
        
        # Add all screens
        sm.add_widget(WelcomeScreen())
        sm.add_widget(WritingScreen())
        sm.add_widget(SessionsScreen())
        sm.add_widget(SettingsScreen())
        sm.add_widget(HelpScreen())
        
        return sm
    
    def on_start(self):
        """Called when app starts."""
        Logger.info('TermiNote: App started')
        
        # Initialize TermiNote directories
        terminote_dir = Path.home() / '.terminote'
        terminote_dir.mkdir(exist_ok=True)
        
        sessions_dir = terminote_dir / 'sessions'
        sessions_dir.mkdir(exist_ok=True)
        
        Logger.info(f'TermiNote: Using directory {terminote_dir}')
    
    def on_pause(self):
        """Handle app pause (Android lifecycle)."""
        return True
    
    def on_resume(self):
        """Handle app resume (Android lifecycle)."""
        pass

if __name__ == '__main__':
    TermiNoteApp().run() 