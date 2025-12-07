# Face Authentication System - User Guide

## Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Using the GUI](#using-the-gui)
4. [Using the CLI](#using-the-cli)
5. [Bash Integration](#bash-integration)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## Installation

### Quick Install

```bash
cd /path/to/linux-hello
./install.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Set up configuration
- Make CLI available

### Manual Install

```bash
# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test
python3 cli.py --help
```

---

## Getting Started

### 1. Enroll Your Face

**Using GUI:**
```bash
./venv/bin/python3 gui.py
```
- Click "Enroll New User" on Dashboard
- Enter your username
- Look at camera and follow prompts
- 5 samples will be captured

**Using CLI:**
```bash
./venv/bin/python3 cli.py enroll $USER
```

### 2. Test Authentication

**GUI:** Click "Test Authentication" button

**CLI:**
```bash
./venv/bin/python3 cli.py test
```

### 3. View Enrolled Users

**GUI:** Go to "Users" tab

**CLI:**
```bash
./venv/bin/python3 cli.py list
```

---

## Using the GUI

### Launching

```bash
cd /path/to/linux-hello
./venv/bin/python3 gui.py
```

### Dashboard Tab
- **System Status**: Shows number of enrolled users
- **Quick Actions**: 
  - Test Authentication
  - Enroll New User
  - Refresh data

### Users Tab
- **View all enrolled users** with sample counts
- **Add User**: Enroll new user with camera
- **Remove User**: Delete user and all samples
- **User Info**: See enrollment date, last seen, sample count

### Samples Tab
- **Select user** from dropdown
- **View samples**: See all face samples for user
- **Add Sample**: Capture additional face sample
- **Remove Sample**: Delete specific sample by index

### Settings Tab
- View current configuration
- Edit `config.yaml` file to change settings
- Click "Reload Settings" after changes

### Logs Tab
- View recent authentication attempts
- See success/failure status
- Check timestamps and usernames

---

## Using the CLI

### User Management

```bash
# Enroll new user
face-auth enroll <username>
face-auth enroll alice --samples 10

# List users
face-auth list

# Remove user
face-auth remove <username>
face-auth remove alice

# Get user info
face-auth info <username>
```

### Sample Management

```bash
# Add sample to existing user
face-auth add-sample <username>

# View samples
face-auth view-samples <username>

# Remove specific sample
face-auth remove-sample <username> <index>

# Export samples
face-auth export-samples <username> <directory>
```

### Authentication

```bash
# Test authentication
face-auth test
face-auth test --timeout 15
face-auth test --no-preview

# Check system status
face-auth status

# View statistics
face-auth stats
```

### System Commands

```bash
# Test camera
face-auth camera-test

# Validate configuration
face-auth validate-config

# Edit configuration
face-auth config edit

# Show configuration
face-auth config show
```

### Monitoring

```bash
# Start monitoring daemon (foreground)
face-auth start-monitor -f

# Start monitoring daemon (background)
face-auth start-monitor

# Stop monitoring daemon
face-auth stop-monitor

# Check daemon status
face-auth status
```

---

## Bash Integration

### Quick Start

```bash
# Source the library
source /path/to/linux-hello/face-auth.sh

# Authenticate
if face_auth 10; then
    echo "Welcome $FACE_AUTH_USER!"
else
    echo "Access denied"
    exit 1
fi
```

### Available Functions

- `face_auth [timeout]` - Authenticate user
- `face_is_enrolled <username>` - Check enrollment
- `face_list_users` - List all users
- `face_enroll <username> [samples]` - Enroll user
- `face_remove <username>` - Remove user
- `face_status` - System status

See [BASH_INTEGRATION.md](../BASH_INTEGRATION.md) for complete guide.

---

## Configuration

### Configuration File

Location: `config.yaml`

### Camera Settings

```yaml
camera:
  device_id: "/dev/video0"
  width: 640
  height: 480
  fps: 30
```

### Recognition Settings

```yaml
recognition:
  tolerance: 0.6  # Lower = stricter (0.4-0.7 recommended)
  model: "hog"    # "hog" (CPU) or "cnn" (GPU)
  num_jitters: 1  # Higher = more accurate but slower
```

### Enrollment Settings

```yaml
enrollment:
  num_samples: 5      # Number of samples to capture
  sample_delay: 1.0   # Seconds between samples
```

### Monitoring Settings

```yaml
monitoring:
  enabled: true
  check_interval: 2.0        # Seconds between checks
  absence_timeout: 30.0      # Seconds before locking
  presence_timeout: 5.0      # Seconds to cancel lock
```

### Actions

```yaml
actions:
  on_absence:
    - lock_screen
  on_presence:
    - log
  on_auth_success:
    - log
  on_auth_failure:
    - log
```

### Security Settings

```yaml
security:
  max_auth_attempts: 3
  lockout_duration: 300      # Seconds
  require_liveness: false    # Anti-spoofing (experimental)
```

---

## Troubleshooting

### Camera Not Working

```bash
# List cameras
ls -l /dev/video*

# Test camera
face-auth camera-test

# Check permissions
groups $USER
# Should include 'video' group

# Add to video group if needed
sudo usermod -a -G video $USER
# Then logout and login
```

### Authentication Fails

**Too strict:**
```yaml
# Edit config.yaml
recognition:
  tolerance: 0.7  # Increase (max 1.0)
```

**Too lenient:**
```yaml
recognition:
  tolerance: 0.5  # Decrease (min 0.0)
```

**Add more samples:**
```bash
face-auth add-sample $USER
```

### Poor Lighting

- Use better lighting
- Add samples in different lighting conditions
- Increase tolerance slightly

### Database Issues

```bash
# Check database
ls -l ~/.local/share/face-auth/

# Backup database
cp ~/.local/share/face-auth/face_auth.db ~/backup.db

# Reset database (WARNING: deletes all users)
rm ~/.local/share/face-auth/face_auth.db
```

### GUI Won't Start

```bash
# Check dependencies
source venv/bin/activate
python3 -c "import tkinter"

# Check logs
python3 gui.py 2>&1 | tee gui.log
```

### CLI Not Found

```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
./venv/bin/python3 cli.py
```

---

## Tips & Best Practices

### Enrollment
- Use good lighting
- Look directly at camera
- Capture samples in different conditions
- Use 5-10 samples for best results

### Authentication
- Position face in center of frame
- Maintain consistent distance
- Avoid extreme angles
- Ensure good lighting

### Security
- Don't rely solely on face auth for critical systems
- Use strong passwords as backup
- Enable liveness detection if needed
- Monitor authentication logs

### Performance
- Use "hog" model for CPU (faster)
- Use "cnn" model for GPU (more accurate)
- Adjust check_interval for monitoring
- Lower tolerance for better security

---

## Next Steps

- [GUI Guide](GUI_GUIDE.md) - Detailed GUI walkthrough
- [PAM Integration](PAM_INTEGRATION.md) - System authentication
- [Bash Integration](../BASH_INTEGRATION.md) - Script integration
- [FAQ](FAQ.md) - Common questions

---

## Support

For issues or questions:
1. Check [FAQ](FAQ.md)
2. Review logs: `~/.local/share/face-auth/face_auth.log`
3. Test camera: `face-auth camera-test`
4. Validate config: `face-auth validate-config`
