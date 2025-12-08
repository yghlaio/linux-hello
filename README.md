<p align="center">
  <h1 align="center">🔐 Linux Hello</h1>
  <p align="center"><strong>Windows Hello™-style Facial Authentication for Linux</strong></p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#cli-reference">CLI Reference</a> •
    <a href="#configuration">Configuration</a> •
    <a href="#documentation">Documentation</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/platform-linux-lightgrey.svg" alt="Platform Linux">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT">
</p>

---

## ⚠️ Important Disclaimers

> **🤖 AI-Generated Code**: This project was created with the assistance of AI (Google Gemini). While functional, it may contain bugs or security issues. Use at your own risk.

> **⚖️ No Warranty**: This software is provided "AS IS" without warranty of any kind, express or implied. See the [LICENSE](LICENSE) file for full details.

> **🔒 Security Notice**: Face recognition is NOT as secure as a password. This is a convenience feature, not a security feature. Always maintain password-based authentication as a fallback.

---

## 🌟 Features

### Core Functionality
- 🔐 **Face Recognition Authentication** - Login using your face instead of passwords
- 👁️ **Continuous Monitoring** - Automatically lock when you walk away
- 🔄 **Rotation-Invariant** - Works even when device rotated 90°/180°/270°
- 🖥️ **GUI Application** - User-friendly Tkinter interface
- 💻 **Complete CLI** - Full command-line interface with all features
- 🔌 **Bash Integration** - Easy shell script integration

### Advanced Features
- 🛡️ **TPM Storage** - Encryption keys in TPM (with file fallback)
- 🔒 **Security Modes** - Fast/Balanced/Secure authentication levels
- 📸 **Sample Management** - Add/remove individual face samples
- 🎯 **Event Hooks** - Custom scripts on presence/absence
- 🔌 **D-Bus IPC** - Integration with other applications
- 🔧 **PAM Support** - System-level authentication (experimental)
- 📊 **Comprehensive Logging** - Complete audit trail

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/linux-hello.git
cd linux-hello

# Run installation script
./install.sh

# Add to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/.local/bin:$PATH"
```

### First Steps

```bash
# 1. Enroll your face (5 samples by default)
face-auth enroll

# 2. Test authentication
face-auth test

# 3. Launch GUI (optional)
./launch-gui.sh
```

---

## 📖 CLI Reference

### User Management

#### `enroll` - Enroll New User

```bash
face-auth enroll [USERNAME] [OPTIONS]
```

**Arguments:**
- `USERNAME` - Username to enroll (default: $USER)

**Options:**
- `--samples N` - Number of face samples to capture (default: 5)
- `--no-preview` - Disable camera preview window

**Examples:**
```bash
# Enroll current user with 5 samples
face-auth enroll

# Enroll specific user with 10 samples
face-auth enroll alice --samples 10

# Enroll without preview (headless)
face-auth enroll --no-preview
```

---

#### `list` - List Enrolled Users

```bash
face-auth list
```

**Output:**
- Username
- Enrollment date
- Last seen timestamp
- Number of samples

**Example:**
```bash
$ face-auth enroll
==========================================
Enrolled Users (2)
==========================================

👤 alice
   Enrolled: 2025-12-07 10:30:15
   Last seen: 2025-12-07 14:25:30

👤 bob
   Enrolled: 2025-12-06 15:20:00
   Last seen: Never
```

---

#### `remove` - Remove User

```bash
face-auth remove USERNAME
```

**Arguments:**
- `USERNAME` - Username to remove

**Example:**
```bash
face-auth remove alice
```

---

### Sample Management

#### `add-sample` - Add Face Sample

```bash
face-auth add-sample USERNAME
```

**Description:** Add additional face sample to existing user for improved accuracy

**Example:**
```bash
# Add sample to improve recognition
face-auth add-sample alice
```

---

#### `view-samples` - View User Samples

```bash
face-auth view-samples USERNAME
```

**Output:** Number of samples and sample indices

**Example:**
```bash
$ face-auth view-samples alice
User: alice
Samples: 7
Indices: 0, 1, 2, 3, 4, 5, 6
```

---

#### `remove-sample` - Remove Specific Sample

```bash
face-auth remove-sample USERNAME INDEX
```

**Arguments:**
- `USERNAME` - Username
- `INDEX` - Sample index (from view-samples)

**Example:**
```bash
# Remove sample at index 3
face-auth remove-sample alice 3
```

---

### Authentication

#### `test` - Test Authentication

```bash
face-auth test [OPTIONS]
```

**Options:**
- `--timeout SECONDS` - Authentication timeout (default: 10)
- `--no-preview` - Disable camera preview

**Examples:**
```bash
# Test with default 10 second timeout
face-auth test

# Test with 15 second timeout
face-auth test --timeout 15

# Test without preview (headless)
face-auth test --no-preview
```

---

### Monitoring

#### `start-monitor` - Start Monitoring Daemon

```bash
face-auth start-monitor [OPTIONS]
```

**Options:**
- `-f, --foreground` - Run in foreground (don't daemonize)

**Description:** Starts continuous presence monitoring. Locks screen when you walk away.

**Examples:**
```bash
# Start as background daemon
face-auth start-monitor

# Run in foreground (for debugging)
face-auth start-monitor -f
```

---

#### `stop-monitor` - Stop Monitoring Daemon

```bash
face-auth stop-monitor
```

**Description:** Stops the monitoring daemon

---

#### `status` - System Status

```bash
face-auth status
```

**Output:**
- Number of enrolled users
- Monitoring daemon status
- D-Bus service status
- Configuration file location

**Example:**
```bash
$ face-auth status
==========================================
Face Authentication System Status
==========================================

Enrolled Users: 2
Monitoring: Running (PID: 12345)
D-Bus Service: Active
Config: ~/.config/face-auth/config.yaml
```

---

### System Commands

#### `camera-test` - Test Camera

```bash
face-auth camera-test
```

**Description:** Lists available cameras and allows testing

**Interactive:**
- Lists all detected cameras
- Shows resolution and FPS
- Allows live testing
- Press 'q' to quit, 's' for snapshot

---

#### `validate-config` - Validate Configuration

```bash
face-auth validate-config
```

**Description:** Checks configuration file for errors

**Output:**
- Configuration file location
- Validation status
- Any errors or warnings

---

#### `config` - Configuration Management

```bash
face-auth config [SUBCOMMAND]
```

**Subcommands:**
- `show` - Display current configuration
- `edit` - Open configuration in editor
- `reload` - Reload configuration

**Examples:**
```bash
# Show current config
face-auth config show

# Edit config in $EDITOR
face-auth config edit

# Reload after manual changes
face-auth config reload
```

---

## ⚙️ Configuration

### Configuration File Location

**Priority order:**
1. `~/.config/face-auth/config.yaml` (user config)
2. `./config.yaml` (project directory - example)

### Complete Configuration Reference

```yaml
# Camera Settings
camera:
  device_id: 0                    # Camera device (int or path)
                                  # Examples: 0, "/dev/video0", 
                                  # "/dev/v4l/by-path/..."
  width: 640                      # Frame width in pixels
  height: 480                     # Frame height in pixels
  fps: 30                         # Frames per second

# Face Recognition Settings
recognition:
  tolerance: 0.6                  # Match tolerance (0.0-1.0)
                                  # Lower = stricter matching
                                  # 0.4 = very strict
                                  # 0.6 = balanced (recommended)
                                  # 0.8 = lenient
  
  model: "hog"                    # Detection model
                                  # "hog" = faster, CPU-based
                                  # "cnn" = more accurate, GPU-based
  
  num_jitters: 1                  # Re-sampling count (1-10)
                                  # Higher = more accurate but slower
                                  # 1 = fast (recommended)
                                  # 5 = very accurate
  
  security_mode: "balanced"       # Security level
                                  # "fast"     - tolerance 0.7, 1 match
                                  # "balanced" - tolerance 0.6, 2 matches
                                  # "secure"   - tolerance 0.5, 3 matches
  
  # Performance tuning
  scale_factor: 0.5               # Downscale for faster detection
                                  # 0.25 = fastest (lower accuracy)
                                  # 0.5 = balanced (recommended)
                                  # 1.0 = full resolution (slowest)
  
  try_rotations: false            # Try 90°/180°/270° rotations
                                  # true = handles rotated camera/device
                                  # false = faster, upright faces only

# Enrollment Settings
enrollment:
  num_samples: 5                  # Samples to capture (3-20)
                                  # 5 = recommended
                                  # 10 = better accuracy
  
  sample_delay: 1.0               # Seconds between samples

# Monitoring Settings
monitoring:
  enabled: true                   # Enable/disable monitoring
  
  check_interval: 2.0             # Seconds between checks
                                  # Lower = more responsive, more CPU
                                  # 2.0 = recommended
                                  # 5.0 = battery saving
  
  absence_timeout: 30.0           # Seconds before lock
                                  # 30 = recommended
                                  # 60 = less aggressive
  
  presence_timeout: 5.0           # Seconds to cancel lock

# Actions
actions:
  on_absence:                     # When user leaves
    - lock_screen                 # Lock the screen
    # - suspend                   # Suspend system
    # - custom_script: /path/to/script.sh
  
  on_presence:                    # When user returns
    - log                         # Log the event
    # - custom_script: /path/to/script.sh
  
  on_auth_success:                # Successful authentication
    - log
  
  on_auth_failure:                # Failed authentication
    - log

# Security Settings
security:
  max_auth_attempts: 3            # Max attempts before lockout
  lockout_duration: 300           # Lockout seconds (5 minutes)
  require_liveness: false         # Anti-spoofing (experimental)
                                  # true = harder to fool with photos
                                  # false = faster, less secure

# Database Settings
database:
  path: "~/.local/share/face-auth/face_auth.db"

# Logging Settings
logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "~/.local/share/face-auth/face_auth.log"
  max_size: 10485760              # 10MB
  backup_count: 3                 # Keep 3 old logs

# D-Bus Settings
dbus:
  enabled: true                   # Enable D-Bus service
  service_name: "org.faceauth.Service"
  object_path: "/org/faceauth/Service"

# Event Hooks (scripts to run)
hooks:
  on_presence: []                 # Scripts on presence
  on_absence: []                  # Scripts on absence
  on_auth_success: []             # Scripts on auth success
  on_auth_failure: []             # Scripts on auth failure
```

### Configuration Examples

#### High Security

```yaml
recognition:
  tolerance: 0.5
  security_mode: "secure"
  num_jitters: 3

security:
  max_auth_attempts: 2
  lockout_duration: 600
  require_liveness: true
```

#### Performance/Battery Saving

```yaml
recognition:
  model: "hog"
  num_jitters: 1

monitoring:
  check_interval: 5.0
  
camera:
  width: 320
  height: 240
```

#### Multiple Cameras

```yaml
camera:
  # Use specific camera by path
  device_id: "/dev/v4l/by-id/usb-Logitech_Webcam-video-index0"
```

---

## 📁 Data Storage

### File Locations

```
~/.local/share/face-auth/
├── face_auth.db              # SQLite database (encrypted)
├── .encryption_key           # Fernet key (or in TPM)
└── face_auth.log             # Application logs

~/.config/face-auth/
└── config.yaml               # User configuration

TPM (if available):
└── NV Index 0x1500000        # Encryption key in TPM
```

### What's Stored

| Data | Location | Encrypted | Description |
|------|----------|-----------|-------------|
| Face encodings | `face_auth.db` | ✅ Yes | 128-D vectors, Fernet encrypted |
| User metadata | `face_auth.db` | ❌ No | Username, dates (not sensitive) |
| Auth logs | `face_auth.db` | ❌ No | Success/fail, timestamps |
| Encryption key | `.encryption_key` or TPM | ❌ No | Fernet key (600 permissions) |
| Configuration | `config.yaml` | ❌ No | User settings |
| Application logs | `face_auth.log` | ❌ No | Debug/info logs |

### Data Privacy

**What's NOT stored:**
- ❌ Raw face images
- ❌ Passwords
- ❌ Unencrypted biometric data
- ❌ Personal information beyond username

---

## 🔐 Security

### ⚠️ Critical Warnings

**This system is NOT as secure as a password!**

- ✅ **DO** use for convenience (screen unlock)
- ✅ **DO** enable password fallback
- ✅ **DO** use `balanced` or `secure` mode
- ❌ **DON'T** use as sole authentication
- ❌ **DON'T** use for root account
- ❌ **DON'T** use for critical systems

### Security Modes Comparison

| Mode | Tolerance | Min Matches | Speed | Security | Use Case |
|------|-----------|-------------|-------|----------|----------|
| **Fast** | 0.7 | 1 sample | ~1-2s | Low | Quick unlock, low risk |
| **Balanced** | 0.6 | 2 samples | ~2-3s | Medium | General use ⭐ |
| **Secure** | 0.5 | 3 samples | ~3-5s | High | Sensitive data |

### TPM Integration

**Trusted Platform Module (TPM) 2.0 Support:**

- Encryption keys stored in TPM NV RAM
- Automatic fallback to file storage
- Transparent to user
- Requires `tpm2-tools` package

**Install TPM tools:**
```bash
# Fedora
sudo dnf install tpm2-tools

# Ubuntu/Debian
sudo apt install tpm2-tools

# Arch
sudo pacman -S tpm2-tools
```

---

## 🎨 GUI Application

### Launch

```bash
./launch-gui.sh
# or
./venv/bin/python3 gui.py
```

### Features

| Tab | Features |
|-----|----------|
| **Dashboard** | System status, quick actions (enroll, test) |
| **Users** | List users, add/remove, view details |
| **Samples** | View samples, add/remove individual samples |
| **Settings** | View configuration, reload settings |
| **Logs** | Authentication history, success/failure |

---

## 🔌 Bash Integration

### Quick Example

```bash
#!/bin/bash
source /path/to/linux-hello/face-auth.sh

# Authenticate with 10 second timeout
if face_auth 10; then
    echo "Welcome $FACE_AUTH_USER!"
    # Protected commands here
else
    echo "Access denied"
    exit 1
fi
```

### Available Functions

```bash
face_auth [timeout]              # Authenticate user
face_is_enrolled <username>      # Check if user enrolled
face_list_users                  # List all users
face_enroll <user> [samples]     # Enroll user
face_remove <username>           # Remove user
face_status                      # System status
```

**See [BASH_INTEGRATION.md](BASH_INTEGRATION.md) for complete guide**

---

## 🐛 Known Issues

### Security Limitations
- ❌ Can be fooled by photos (liveness detection experimental)
- ❌ Similar faces may authenticate
- ⚠️ Not password-equivalent security

### Hardware Limitations
- ❌ No IR camera support (unlike Howdy)
- ⚠️ Some USB cameras may not work
- ⚠️ Performance varies (1-10s depending on hardware)

### Software Limitations
- ⚠️ Python 3.14 compatibility (workarounds in place)
- ⚠️ Memory usage (~200MB + 50MB/user)
- ⚠️ CPU-intensive during recognition

**See [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) for complete list**

---

## 📚 Documentation

- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete user manual
- **[FAQ.md](docs/FAQ.md)** - Frequently asked questions
- **[PAM_INTEGRATION.md](docs/PAM_INTEGRATION.md)** - System authentication
- **[BASH_INTEGRATION.md](BASH_INTEGRATION.md)** - Shell script integration
- **[KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)** - Limitations and bugs
- **[TESTING.md](TESTING.md)** - Testing guide

---

## 🛠️ Installation & Removal

### Install

```bash
./install.sh
```

**What it does:**
1. Creates Python virtual environment
2. Installs dependencies
3. Sets up configuration
4. Creates CLI wrapper in `~/.local/bin`

### Uninstall

```bash
# Remove user data
rm -rf ~/.local/share/face-auth/
rm -rf ~/.config/face-auth/

# Remove CLI
rm ~/.local/bin/face-auth

# Remove venv
rm -rf venv/

# Optional: Remove PAM
cd pam/ && sudo ./uninstall_pam.sh
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Make changes and test
4. Commit (`git commit -m 'Add amazing feature'`)
5. Push (`git push origin feature/amazing`)
6. Open Pull Request

**Run tests before submitting:**
```bash
./run_tests.sh
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for full details.

**Key Points:**
- ✅ Free to use, modify, and distribute
- ✅ Commercial use allowed
- ⚠️ Provided "AS IS" without warranty
- ⚠️ AI-generated code - review before use
- ⚠️ Not suitable as primary security measure

---

## 🙏 Acknowledgments

- **face_recognition** by Adam Geitgey
- **dlib** by Davis King
- **Howdy** project for inspiration
- OpenCV community

---

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/YOUR_USERNAME/linux-hello/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/linux-hello/discussions)

---

<p align="center">
  <strong>⚠️ Remember: Use for convenience, not security. Always enable password fallback!</strong>
</p>

<p align="center">
  Made with ❤️ for the Linux community
</p>
