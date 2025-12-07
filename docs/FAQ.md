# Frequently Asked Questions (FAQ)

## General Questions

### What is this system?
A Linux face authentication system similar to Windows Hello. It allows you to login and authenticate using facial recognition instead of (or in addition to) passwords.

### Is it secure?
Face recognition is convenient but not as secure as a strong password. Use it for:
- ✅ Screen unlock
- ✅ Quick authentication
- ✅ Convenience features
- ❌ Root access (not recommended)
- ❌ Critical systems (use password)

### What Linux distributions are supported?
Any Linux distribution with:
- Python 3.8+
- Webcam support
- systemd (optional, for monitoring daemon)

Tested on: Fedora, Ubuntu, Arch Linux

---

## Installation & Setup

### Do I need a special camera?
No, any standard webcam works. USB webcams, built-in laptop cameras, etc.

### Can I use multiple cameras?
Yes, configure the device in `config.yaml`:
```yaml
camera:
  device_id: "/dev/video0"  # or /dev/video1, etc.
```

### Installation fails with "dlib" error
dlib requires compilation. Install build dependencies:
```bash
# Fedora
sudo dnf install gcc-c++ cmake python3-devel

# Ubuntu/Debian
sudo apt install build-essential cmake python3-dev

# Then retry
pip install dlib
```

### How much disk space is needed?
- Base installation: ~500MB (mostly dlib/opencv)
- Per user: ~10KB (encrypted face data)
- Logs: Configurable, default 10MB max

---

## Usage

### How many face samples should I capture?
- **Minimum**: 3 samples
- **Recommended**: 5-10 samples
- **Maximum**: No limit, but diminishing returns after 15

More samples = better accuracy in varying conditions.

### Can I enroll multiple people?
Yes! Each user has their own face data. Useful for:
- Family computers
- Shared workstations
- Multi-user systems

### What if my appearance changes?
- **Minor changes** (haircut, glasses): Usually still works
- **Major changes** (beard, significant weight): Add new samples or re-enroll

```bash
# Add samples
face-auth add-sample $USER

# Or re-enroll
face-auth remove $USER
face-auth enroll $USER
```

### Does it work in the dark?
No, face recognition requires visible light. Minimum lighting needed:
- Indoor lighting (normal room lights)
- Natural daylight
- Does NOT work in complete darkness

### Can someone use my photo to login?
**Basic mode**: Possibly, photos might work
**With liveness detection**: Much harder, but not impossible

Enable liveness detection:
```yaml
# config.yaml
security:
  require_liveness: true
```

Note: Liveness detection is experimental and may reduce accuracy.

---

## Configuration

### How do I adjust sensitivity?
Edit `config.yaml`:
```yaml
recognition:
  tolerance: 0.6  # Lower = stricter, Higher = more lenient
```

- **0.4**: Very strict (may reject you sometimes)
- **0.6**: Balanced (recommended)
- **0.8**: Lenient (may accept similar faces)

### Can I change the number of samples during enrollment?
Yes:
```bash
# CLI
face-auth enroll alice --samples 10

# Or edit config.yaml
enrollment:
  num_samples: 10
```

### How do I change the camera?
```bash
# List cameras
ls -l /dev/video*

# Edit config.yaml
camera:
  device_id: "/dev/video1"  # Change number
```

### Where is my data stored?
- **Face data**: `~/.local/share/face-auth/face_auth.db` (encrypted)
- **Encryption key**: `~/.local/share/face-auth/.encryption_key`
- **Logs**: `~/.local/share/face-auth/face_auth.log`
- **Config**: `<project-dir>/config.yaml`

---

## Monitoring Daemon

### What does the monitoring daemon do?
Continuously watches for your presence:
- **Present**: Logs your presence
- **Absent** (30s): Locks screen automatically

### How do I start monitoring?
```bash
# Foreground (for testing)
face-auth start-monitor -f

# Background (normal use)
face-auth start-monitor

# As systemd service
systemctl --user enable face-auth-monitor
systemctl --user start face-auth-monitor
```

### How do I stop monitoring?
```bash
face-auth stop-monitor

# Or
systemctl --user stop face-auth-monitor
```

### Can I change the timeout?
Edit `config.yaml`:
```yaml
monitoring:
  absence_timeout: 60.0  # Seconds before locking (default: 30)
  check_interval: 5.0    # Seconds between checks (default: 2)
```

---

## PAM Integration

### What is PAM integration?
Allows face authentication for:
- System login (GDM, LightDM, etc.)
- sudo commands
- Screen unlock
- su (switch user)

### Is PAM integration safe?
**With precautions, yes:**
- Password fallback always available
- Backup your PAM config
- Test in VM first
- Keep recovery access

**See [PAM_INTEGRATION.md](PAM_INTEGRATION.md) for details.**

### Will I be locked out if face auth fails?
No! PAM is configured with "sufficient":
- Face auth succeeds → Login immediately
- Face auth fails → Try password

### Can I use face auth for root?
**Not recommended!** Use for regular user accounts only. Root should always require password.

---

## Troubleshooting

### "Camera not found" error
```bash
# Check camera exists
ls -l /dev/video*

# Check permissions
groups $USER  # Should include 'video'

# Add to video group
sudo usermod -a -G video $USER
# Logout and login

# Test camera
face-auth camera-test
```

### "No face detected"
- Ensure good lighting
- Position face in center
- Move closer/farther from camera
- Remove obstructions (hands, hair)
- Check camera is working: `cheese` or `guvcview`

### Authentication too slow
```yaml
# config.yaml
recognition:
  model: "hog"  # Faster (CPU)
  # vs
  model: "cnn"  # Slower but more accurate (GPU)
```

### "User not enrolled"
```bash
# Check enrolled users
face-auth list

# Enroll if missing
face-auth enroll $USER
```

### GUI won't start
```bash
# Check tkinter
python3 -c "import tkinter; print('OK')"

# Install if missing (Fedora)
sudo dnf install python3-tkinter

# Install if missing (Ubuntu)
sudo apt install python3-tk
```

### Database corrupted
```bash
# Backup first
cp ~/.local/share/face-auth/face_auth.db ~/backup.db

# Reset (WARNING: deletes all users)
rm ~/.local/share/face-auth/face_auth.db
rm ~/.local/share/face-auth/.encryption_key

# Re-enroll
face-auth enroll $USER
```

---

## Performance

### How fast is authentication?
- **hog model (CPU)**: 1-3 seconds
- **cnn model (GPU)**: 2-5 seconds
- Depends on: CPU/GPU, resolution, number of enrolled users

### Does it use a lot of CPU?
- **Idle**: Minimal (no monitoring)
- **Monitoring**: Low (~5-10% CPU every 2 seconds)
- **Authentication**: High (brief spike during recognition)

### Can I use it on a Raspberry Pi?
Yes, but:
- Use "hog" model (CPU)
- Expect slower performance
- May need to increase timeout
- Reduce resolution if needed

---

## Privacy & Security

### Is my face data encrypted?
Yes! Face encodings are encrypted using Fernet (symmetric encryption) before storage.

### Where is the encryption key?
`~/.local/share/face-auth/.encryption_key`

**Protect this file!** Without it, face data cannot be decrypted.

### Can I export my face data?
```bash
# Export samples (as numpy arrays)
face-auth export-samples $USER ~/my-samples/

# Backup database
cp ~/.local/share/face-auth/face_auth.db ~/backup.db
cp ~/.local/share/face-auth/.encryption_key ~/backup.key
```

### Is authentication logged?
Yes, all attempts logged to:
- Application log: `~/.local/share/face-auth/face_auth.log`
- System log (PAM): `/var/log/auth.log`

### Can I disable logging?
Not recommended, but edit `config.yaml`:
```yaml
logging:
  level: "ERROR"  # Only log errors
```

---

## Advanced

### Can I use this over SSH?
No, requires local camera access. SSH is text-only.

### Can I integrate with my own scripts?
Yes! See [BASH_INTEGRATION.md](../BASH_INTEGRATION.md)

```bash
source face-auth.sh
if face_auth; then
    echo "Authenticated as $FACE_AUTH_USER"
fi
```

### Can I use a different database?
Currently SQLite only. PostgreSQL/MySQL support could be added.

### Can I run multiple instances?
Yes, use different config files:
```bash
FACE_AUTH_CONFIG=/path/to/config.yaml face-auth enroll alice
```

### How do I contribute?
This is a personal project, but:
- Report bugs
- Suggest features
- Submit pull requests
- Share improvements

---

## Comparison

### vs Windows Hello
**Similarities:**
- Face recognition for login
- Encrypted biometric data
- Fast authentication

**Differences:**
- Windows Hello: Integrated into OS
- This system: Standalone, more configurable
- Windows Hello: IR camera support
- This system: Standard webcam

### vs Fingerprint
**Face Auth Pros:**
- No special hardware needed
- Contactless
- Works from distance

**Face Auth Cons:**
- Requires lighting
- Can be fooled by photos (without liveness)
- Affected by appearance changes

**Fingerprint Pros:**
- More secure
- Works in dark
- Not affected by appearance

**Fingerprint Cons:**
- Requires fingerprint reader
- Contact required
- Can be dirty/wet

---

## Getting Help

### Where can I find more documentation?
- [USER_GUIDE.md](USER_GUIDE.md) - Complete user guide
- [GUI_GUIDE.md](GUI_GUIDE.md) - GUI walkthrough
- [PAM_INTEGRATION.md](PAM_INTEGRATION.md) - System integration
- [BASH_INTEGRATION.md](../BASH_INTEGRATION.md) - Script integration
- [README.md](../README.md) - Project overview

### How do I report a bug?
1. Check this FAQ first
2. Review logs: `~/.local/share/face-auth/face_auth.log`
3. Test with: `face-auth validate-config`
4. Gather system info: `face-auth status`

### How do I request a feature?
Open an issue with:
- Feature description
- Use case
- Why it's useful

---

## Quick Reference

```bash
# Enrollment
face-auth enroll $USER
face-auth add-sample $USER

# Authentication
face-auth test

# Management
face-auth list
face-auth remove $USER
face-auth info $USER

# Samples
face-auth view-samples $USER
face-auth remove-sample $USER 0

# System
face-auth status
face-auth camera-test
face-auth validate-config

# GUI
python3 gui.py

# Monitoring
face-auth start-monitor
face-auth stop-monitor
```
