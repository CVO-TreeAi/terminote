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

## 🚀 Quick Start

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/yourusername/terminote.git
cd terminote

# Install NEO command globally (creates virtual environment + dependencies)
./install.sh
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

# Quick shortcuts
neo s           # Sessions
neo c           # Config
neo w           # Quick work menu
```

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
python3 cli.py --help
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
   git remote add origin https://github.com/yourusername/terminote.git
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
