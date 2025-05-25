# TermiNote v5 🏠 NEO

An AI-native CLI for focused writing, dev planning, and document generation powered by OpenRouter.

**Meet NEO** - Your AI writing assistant who lives in TermiNote and helps you turn ideas into reality.

## 🌟 Features

- **✍️ AI-Powered Writing Sessions** - Interactive writing with real-time AI assistance
- **🏗️ Project Planning Mode** - Comprehensive development planning and task breakdown  
- **📝 Document Generation** - Generate READMEs, specs, API docs, and guides
- **💾 Session Management** - Auto-save, resume, and export your work
- **🔧 Multi-Model Support** - Use Claude, GPT-4, Llama, and other models via OpenRouter
- **🎨 Beautiful Terminal UI** - Rich formatting with syntax highlighting
- **📱 Native Android App** - Touch-optimized GUI with dual-mode support (GUI + Terminal)
- **🤖 Dual-Mode Operation** - Seamlessly switch between GUI and CLI interfaces
- **🔄 Cross-Platform Sync** - Same core experience across desktop, mobile, and tablet

## 🚀 Quick Start

### 1. Clone and Install

**On macOS/Linux:**
```bash
# Clone the repository
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote

# Install NEO command globally (creates virtual environment + dependencies)
./install.sh
```

**On Android (Termux):**
```bash
# First, install required packages
pkg update && pkg install python git

# Clone the repository
git clone https://github.com/CVO-TreeAi/terminote.git
cd terminote

# Use the Termux-specific installer (recommended)
chmod +x install-termux.sh
./install-termux.sh

# Or use the universal installer
# ./install.sh
```

**📱 Android App (Native GUI):**
```bash
# Option 1: Download latest APK from releases
wget https://github.com/CVO-TreeAi/terminote/releases/latest/download/terminote-release.apk
adb install terminote-release.apk

# Option 2: Build from source
cd terminote/android
./install-android-dev.sh  # Setup development environment
./build-android.sh debug  # Build APK
adb install bin/terminote-*-debug.apk
```

### 2. Configure Your API Key
```bash
# Run initial setup to configure your OpenRouter API key
neo setup
```

You'll need an [OpenRouter API key](https://openrouter.ai/keys) to use NEO. Each installation is unique - your API key stays private on your device.

### 3. Start Working with NEO!
```bash
# Quick work menu
neo

# Or jump directly to what you need
neo write          # Start writing
neo project        # Plan a project
neo generate readme # Generate docs
```

## 📖 Usage

### Writing Mode
```bash
neo write [session-name]
```

**Commands in writing mode:**
- `/continue [direction]` - AI continues your writing
- `/suggest` - Get AI suggestions for improvement  
- `/outline [topic]` - Generate an outline
- `/brainstorm [topic]` - Brainstorm ideas
- `/export` - Export to file
- `/save` - Save session
- `/help` - Show all commands

### Project Mode
```bash
neo project [project-name]
```

**Commands in project mode:**
- `/plan [description]` - Generate development plan
- `/tasks` - Break down into tasks
- `/docs [type]` - Generate documentation
- `/code-review` - Interactive code review
- `/help` - Show all commands

### Document Generation
```bash
neo generate <type> [output-path]
```

**Document types:**
- `readme` - Project README files
- `spec` - Technical specifications
- `api-docs` - API documentation
- `guide` - User guides

### Session Management
```bash
neo sessions     # List all sessions
neo config       # View configuration
neo doctor       # System health check and diagnostics

# Quick shortcuts
neo s           # Sessions
neo c           # Config
neo w           # Quick work menu
```

### 📱 Android App Usage

**Dual-Mode Launcher:**
```bash
# Auto-detect best interface for environment
python android/launcher.py

# Force specific mode
python android/launcher.py gui      # GUI app
python android/launcher.py cli      # Terminal CLI
```

**GUI App Features:**
- **Touch-optimized interface** with large buttons and scroll areas
- **Session browser** with visual session management
- **Chat mode toggle** - switch between writing and AI chat
- **Export to Downloads** folder with Android sharing integration
- **Auto-save** and session recovery

**Termux Integration:**
- **Full CLI compatibility** in Termux terminal
- **GUI option** when X11 or VNC is available
- **Shared session storage** between GUI and CLI modes
- **Environment detection** - automatically chooses best interface

## ⚙️ Configuration

TermiNote stores configuration in `~/.terminote/`:
- `config.yaml` - Settings and model preferences  
- `.env` - API keys (encrypted)
- `sessions/` - Writing sessions
- `prompts/` - Custom prompt templates

### Model Selection

Configure different models for different tasks:
- **Writing**: Creative writing and content generation
- **Coding**: Development planning and code review
- **Quick**: Fast responses and simple tasks

Supported models include:
- Claude 3.5 Sonnet/Opus/Haiku (Anthropic)
- GPT-4o/4o-mini (OpenAI)
- Llama 3.1 (Meta)
- Gemini Pro (Google)
- Mistral Large (Mistral)

## 🔧 Advanced Usage

### Custom Prompts
Add custom prompts in `~/.terminote/prompts/` or `prompts/`:
```markdown
# my-prompt.md
You are an expert {role} assistant...
```

Use with variable substitution:
```python
prompt_engine.get_prompt('my-prompt', {'role': 'developer'})
```

### Environment Variables
```bash
export OPENROUTER_API_KEY="your-key-here"
export EDITOR="code"  # Default editor for file editing
```

### Virtual Environment
TermiNote uses its own virtual environment. To manually activate:
```bash
source venv/bin/activate
python cli.py --help  # Use 'python' inside venv (works on all platforms)
```

### Termux (Android) Support
TermiNote fully supports Android via Termux:
- **Automatic detection** of Termux environment
- **No sudo required** - installs to `$PREFIX/bin`
- **Python compatibility** - works with Termux's Python installation
- **Full feature support** - all NEO features available on mobile

**Termux requirements:**
```bash
pkg install python git
```

## 📁 Project Structure

```
terminote/
├── cli.py              # Main CLI entry point
├── core/               # Core modules
│   ├── ai_client.py    # OpenRouter integration
│   ├── config_manager.py # Configuration management
│   ├── router.py       # Mode routing and UI
│   ├── session.py      # Session management
│   └── prompt_engine.py # Prompt templates
├── tools/              # Utility tools
│   ├── docbuilder.py   # Document generation
│   └── file_editor.py  # File operations
├── prompts/            # Default prompt templates
├── bin/scribe          # Alternative entry script
├── terminote.sh        # Activation script
└── requirements.txt    # Dependencies
```

## 🚀 For Repository Owners

To create your own public repository:

1. Create a new repository on GitHub (public)
2. Add the remote origin:
   ```bash
   git remote add origin https://github.com/CVO-TREEAI/terminote.git
   git branch -M main
   git push -u origin main
   ```

3. Update the clone URL in README.md to match your repository

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs or request features on GitHub
- **Documentation**: Check prompts/ for examples
- **API Keys**: Get OpenRouter access at https://openrouter.ai

---

Made with ❤️ for writers and developers who want AI-powered productivity without the complexity.
