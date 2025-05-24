# Error Handling & Troubleshooting Guide

TermiNote v5 includes comprehensive error handling designed to work seamlessly across both macOS and Android (Termux) platforms.

## 🛡️ Error Handling Architecture

### Centralized Error Management
- **Location**: `core/error_handler.py`
- **Purpose**: Unified error handling with platform-specific guidance
- **Features**: 
  - Rich formatting with color-coded severity levels
  - Platform-specific troubleshooting advice
  - Debug logging when enabled
  - Graceful degradation for non-critical errors

### Error Types & Severity Levels

| Error Type | Severity | Description | Example |
|------------|----------|-------------|---------|
| `ConfigurationError` | ⚠️ Warning | Missing/invalid config | No API key set |
| `APIError` | ⚠️ Warning | OpenRouter API issues | Network timeout |
| `SessionError` | ❌ Error | Session file problems | Corrupted JSON |
| `PlatformError` | ❌ Error | OS-specific issues | Permission denied |
| `Exception` | 💥 Critical | Unexpected errors | Python crashes |

## 📱 Platform-Specific Handling

### macOS Support
```python
# Automatic detection
if platform.system() == 'Darwin':
    # macOS-specific error guidance
    return "• On macOS: Try with sudo or check file permissions"
```

**Common macOS Issues:**
- **Permission Denied**: Check Terminal disk access in System Preferences
- **Virtual Environment**: Install Python via Homebrew or python.org
- **Network Issues**: Check firewall settings

### Android/Termux Support
```python
# Automatic detection
if 'TERMUX_VERSION' in os.environ:
    # Termux-specific error guidance
    return "• On Termux: Check storage permissions\n• Run: termux-setup-storage"
```

**Common Termux Issues:**
- **Storage Access**: Run `termux-setup-storage` for file permissions
- **Network Issues**: Check app permissions in Android settings
- **Package Missing**: Use `pkg install <package-name>`
- **File Paths**: Use full paths starting with `/data/data/com.termux/`

## 🩺 Health Check System

### Running Diagnostics
```bash
# Run comprehensive system check
neo doctor

# Alternative commands
neo health
neo check
```

### Health Check Components

1. **Python Environment**
   - Version compatibility (3.8+)
   - Required modules availability
   - Virtual environment status

2. **File Permissions**
   - Config directory access
   - Session storage write access
   - Log file creation

3. **Configuration**
   - API key validation
   - Model configuration
   - Preferences setup

4. **Session Storage**
   - File creation/loading test
   - JSON serialization test
   - Cleanup verification

5. **Network Access**
   - OpenRouter API connectivity
   - General internet access
   - Timeout handling

6. **Platform Features**
   - Terminal capabilities
   - Process execution
   - Platform-specific tools

## 🔧 Error Recovery Patterns

### Automatic Recovery
```python
# Session loading with fallback
try:
    session = load_session(name)
except (json.JSONDecodeError, FileNotFoundError):
    # Automatically create new session
    session = create_empty_session(name)
```

### Backup & Restore
```python
# Session save with backup
if session_file.exists():
    backup_file = session_file.with_suffix('.bak')
    session_file.rename(backup_file)

# Restore on failure
if save_failed and backup_file.exists():
    backup_file.rename(session_file)
```

## 🐛 Debug Mode

### Enable Debug Logging
```bash
# Enable detailed error logging
export TERMINOTE_DEBUG=1
neo write

# Check debug logs
cat ~/.terminote/logs/errors.log
```

### Debug Information Includes
- Full stack traces
- Platform details
- Environment variables
- File system context
- Network connectivity details

## 🚨 Common Error Scenarios

### 1. First Time Setup Issues

**Symptom**: "No OpenRouter API key found"
```bash
# Solution
neo setup
# Enter your API key from https://openrouter.ai/keys
```

**Platform-Specific Notes:**
- **macOS**: May require Terminal disk access permission
- **Termux**: Ensure storage setup with `termux-setup-storage`

### 2. Permission Denied Errors

**macOS**:
```bash
# Check Terminal permissions
# System Preferences > Security & Privacy > Privacy > Full Disk Access
# Add Terminal.app

# Or run with sudo
sudo neo setup
```

**Termux**:
```bash
# Setup storage access
termux-setup-storage

# Check file permissions
ls -la ~/.terminote/
```

### 3. Network/API Errors

**General**:
```bash
# Test connection
neo doctor

# Check API key
neo setup
```

**Termux-Specific**:
```bash
# Check network permission in Android settings
# Settings > Apps > Termux > Permissions > Network

# Test basic connectivity
ping google.com
```

### 4. Virtual Environment Issues

**macOS**:
```bash
# Reinstall with proper Python
brew install python3
cd terminote
./install.sh
```

**Termux**:
```bash
# Update packages
pkg update && pkg upgrade

# Reinstall Python
pkg install python
cd terminote
./install-termux.sh
```

### 5. Session File Corruption

**Symptoms**: "Error loading session" or JSON decode errors

**Recovery**:
```bash
# Check for backup files
ls ~/.terminote/sessions/*.bak

# Manual recovery
cd ~/.terminote/sessions/
cp session_name.bak session_name.json

# Or create new session
neo write  # Will auto-create new session
```

## 📊 Error Statistics & Monitoring

### Health Check Results Interpretation

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| 7/7 ✅ | Perfect health | None |
| 5-6/7 ⚠️ | Minor issues | Check warnings |
| <5/7 ❌ | Needs attention | Run troubleshooting |

### Log Analysis
```bash
# View recent errors
tail -20 ~/.terminote/logs/errors.log

# Search for specific errors
grep "Permission denied" ~/.terminote/logs/errors.log

# Clear old logs
rm ~/.terminote/logs/errors.log
```

## 🔄 Error Handling Best Practices

### For Developers

1. **Use Centralized Error Handling**:
```python
from core.error_handler import error_handler, safe_execute

# Wrap risky operations
result = safe_execute(
    risky_function,
    context="Feature name",
    user_message="User-friendly description"
)
```

2. **Custom Error Types**:
```python
from core.error_handler import SessionError

if invalid_session:
    raise SessionError("Session file is corrupted")
```

3. **Platform-Aware Error Messages**:
```python
if self.is_termux:
    guidance = "On Termux: pkg install python"
elif self.is_macos:
    guidance = "On macOS: brew install python3"
```

### For Users

1. **Always Run Health Check First**:
```bash
neo doctor  # Diagnoses most issues automatically
```

2. **Enable Debug Mode for Complex Issues**:
```bash
export TERMINOTE_DEBUG=1
neo write  # Now shows detailed error info
```

3. **Check Platform-Specific Documentation**:
- macOS: Focus on permissions and Homebrew
- Termux: Focus on storage setup and pkg management

## 🆘 Getting Help

### Before Reporting Issues

1. **Run Health Check**: `neo doctor`
2. **Check Debug Logs**: `cat ~/.terminote/logs/errors.log`
3. **Verify Installation**: `./install.sh` (or `./install-termux.sh`)
4. **Test Network**: Try `neo setup` to verify API connectivity

### Reporting Issues

Include in your bug report:
- Health check output (`neo doctor`)
- Platform details (macOS version or Termux info)
- Error logs (with sensitive info removed)
- Steps to reproduce

### Quick Links
- **GitHub Issues**: https://github.com/CVO-TreeAi/terminote/issues
- **Documentation**: README.md
- **API Keys**: https://openrouter.ai/keys

---

*TermiNote v5 Error Handling - Designed for reliability across platforms* 🛡️ 