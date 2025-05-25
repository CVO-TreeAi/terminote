"""
TermiNote Android App - Native Android version with GUI
Built with Kivy for cross-platform mobile development
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for importing core modules
app_root = Path(__file__).parent.parent
sys.path.insert(0, str(app_root))

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

# Import TermiNote core modules
from core.session import SessionManager
from core.ai_client import OpenRouterClient
from core.config_manager import ConfigManager
from core.error_handler import error_handler

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
            ('Project Mode', self.project_mode),
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
        
        self.add_widget(layout)
    
    def start_writing(self, instance):
        self.manager.current = 'writing'
    
    def continue_session(self, instance):
        self.manager.current = 'sessions'
    
    def project_mode(self, instance):
        self.manager.current = 'project'
    
    def sessions_manager(self, instance):
        self.manager.current = 'sessions'
    
    def settings(self, instance):
        self.manager.current = 'settings'
    
    def help(self, instance):
        self.manager.current = 'help'

class WritingScreen(Screen):
    """Main writing interface with AI chat toggle."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'writing'
        self.session_manager = SessionManager()
        self.ai_client = OpenRouterClient()
        self.current_session = None
        self.chat_mode = False
        
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Top bar with session info and controls
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        self.session_label = Label(text='No Session', size_hint_x=0.5)
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
            text='Start writing here...',
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
        if self.current_session:
            content = self.text_input.text
            self.current_session['content'] = content
            self.current_session['word_count'] = len(content.split())
            
            success = self.session_manager.save_session(
                self.current_session['name'], 
                self.current_session
            )
            
            if success:
                self.show_popup('Success', 'Session saved!')
            else:
                self.show_popup('Error', 'Failed to save session')
    
    def ai_suggest(self, instance):
        """Get AI suggestions for current text."""
        if not self.text_input.text.strip():
            self.show_popup('Info', 'Write something first for AI to help with!')
            return
        
        # Simple AI interaction - in chat mode, treat as chat
        if self.chat_mode:
            self.handle_ai_chat()
        else:
            self.handle_ai_suggestions()
    
    def handle_ai_chat(self):
        """Handle AI chat interaction."""
        user_input = self.text_input.text.strip()
        if not user_input:
            return
        
        # Add user message to chat
        chat_text = f"\n[You]: {user_input}\n[AI]: "
        
        # Get AI response (simplified for demo)
        try:
            messages = [
                {"role": "system", "content": "You are NEO, a helpful writing assistant in TermiNote."},
                {"role": "user", "content": user_input}
            ]
            
            response = ""
            for chunk in self.ai_client.chat_completion(messages, stream=True):
                response += chunk
            
            chat_text += response + "\n"
            self.text_input.text = chat_text
            
        except Exception as e:
            self.show_popup('Error', f'AI Error: {str(e)}')
    
    def handle_ai_suggestions(self):
        """Handle AI writing suggestions."""
        content = self.text_input.text
        
        try:
            suggestions = ""
            for chunk in self.ai_client.get_writing_suggestions(content):
                suggestions += chunk
            
            # Show suggestions in popup
            self.show_popup('AI Suggestions', suggestions)
            
        except Exception as e:
            self.show_popup('Error', f'AI Error: {str(e)}')
    
    def export_session(self, instance):
        """Export current session."""
        if self.current_session:
            # On Android, save to Downloads folder
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            
            export_path = f"/storage/emulated/0/Download/{self.current_session['name']}.md"
            success = self.session_manager.export_session(self.current_session['name'], export_path)
            
            if success:
                self.show_popup('Success', f'Exported to Downloads/{self.current_session["name"]}.md')
            else:
                self.show_popup('Error', 'Export failed')
    
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
        self.session_manager = SessionManager()
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
        self.sessions_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.sessions_layout.bind(minimum_height=self.sessions_layout.setter('height'))
        scroll.add_widget(self.sessions_layout)
        layout.add_widget(scroll)
        
        # Load sessions
        self.load_sessions()
        
        self.add_widget(layout)
    
    def load_sessions(self):
        """Load and display sessions list."""
        self.sessions_layout.clear_widgets()
        
        sessions = self.session_manager.list_sessions()
        
        for session in sessions:
            session_item = BoxLayout(
                orientation='horizontal', 
                size_hint_y=None, 
                height='60dp',
                spacing=10
            )
            
            # Session info
            info_text = f"{session['name']}\n{session['word_count']} words"
            info_label = Label(
                text=info_text,
                size_hint_x=0.6,
                halign='left'
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
                font_size='14sp'
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
        # Simple confirmation - in real app, use proper dialog
        self.session_manager.delete_session(session_name)
        self.load_sessions()  # Refresh list
    
    def go_back(self, instance):
        self.manager.current = 'welcome'

class SettingsScreen(Screen):
    """App settings and configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.config = ConfigManager()
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
        
        # Other settings
        layout.add_widget(Label(text='App Information:', size_hint_y=None, height='30dp'))
        layout.add_widget(Label(
            text='TermiNote v5.0\nAI Writing Assistant\nAndroid Native App',
            size_hint_y=None,
            height='80dp'
        ))
        
        self.add_widget(layout)
    
    def save_settings(self, instance):
        """Save API key and other settings."""
        api_key = self.api_key_input.text.strip()
        if api_key:
            # Save API key to config
            os.environ['OPENROUTER_API_KEY'] = api_key
            
            popup = Popup(
                title='Success',
                content=Label(text='Settings saved!'),
                size_hint=(0.6, 0.3)
            )
            popup.open()
    
    def go_back(self, instance):
        self.manager.current = 'welcome'

class TermiNoteApp(App):
    """Main TermiNote Android application."""
    
    def build(self):
        """Build the app interface."""
        # Set up screen manager
        sm = ScreenManager()
        
        # Add all screens
        sm.add_widget(WelcomeScreen())
        sm.add_widget(WritingScreen())
        sm.add_widget(SessionsScreen())
        sm.add_widget(SettingsScreen())
        
        return sm
    
    def on_start(self):
        """Called when app starts."""
        Logger.info('TermiNote: App started')
        
        # Initialize TermiNote directories
        terminote_dir = Path.home() / '.terminote'
        terminote_dir.mkdir(exist_ok=True)
        
        # Check if first run
        config = ConfigManager()
        if not config.get_api_key():
            Logger.info('TermiNote: First run - showing setup')
    
    def on_pause(self):
        """Handle app pause (Android lifecycle)."""
        return True
    
    def on_resume(self):
        """Handle app resume (Android lifecycle)."""
        pass

if __name__ == '__main__':
    TermiNoteApp().run() 