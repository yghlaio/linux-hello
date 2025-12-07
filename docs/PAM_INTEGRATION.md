# PAM Integration Guide

## ⚠️ IMPORTANT WARNING

**PAM (Pluggable Authentication Modules) integration modifies system authentication. Incorrect configuration can lock you out of your system!**

- Always have a backup login method
- Test in a virtual machine first
- Keep a root terminal open during testing
- Know how to boot into recovery mode

---

## What is PAM?

PAM is Linux's authentication framework. Integrating face authentication with PAM allows you to use face recognition for:
- System login (GDM, LightDM, SDDM)
- sudo commands
- Screen unlock
- su (switch user)

---

## Prerequisites

1. **Enrolled face data**: Enroll yourself first using the GUI or CLI
2. **Working camera**: Test with `face-auth test`
3. **Backup access**: Another user account or SSH access
4. **python-pam**: Already in requirements.txt

---

## Installation Steps

### 1. Test Face Authentication First

```bash
cd /path/to/linux-hello

# Enroll yourself
./venv/bin/python3 cli.py enroll $USER

# Test authentication
./venv/bin/python3 cli.py test
```

Make sure authentication works reliably before proceeding!

### 2. Review PAM Module

The PAM module is located at `pam/pam_face_auth.py`. It:
- Attempts face authentication first
- Falls back to password if face auth fails
- Logs all attempts to syslog
- Has a 15-second timeout

### 3. Run Installation Script

**⚠️ CRITICAL: Keep this terminal open as backup!**

```bash
cd /path/to/linux-hello/pam

# Review the script first
cat install_pam.sh

# Run as root
sudo ./install_pam.sh
```

The script will:
1. Check dependencies
2. Install PAM module to `/lib/security/`
3. Backup existing PAM configuration
4. Configure GDM and sudo
5. Show backup location

### 4. Test in New Terminal

**DO NOT close your current terminal!**

Open a new terminal and test:

```bash
# Test sudo
sudo echo "Testing sudo with face auth"

# You should see camera activate
# Face auth will attempt first
# Password will be asked if face auth fails
```

### 5. Test Login

**Only after sudo works:**

1. Lock your screen (Super+L)
2. Try to unlock with face
3. Verify password fallback works

---

## Configuration

### PAM Configuration Files

The installation modifies:
- `/etc/pam.d/gdm-password` - Display manager login
- `/etc/pam.d/sudo` - sudo authentication

Example configuration line:
```
auth    sufficient    pam_python.so pam_face_auth.py
```

**sufficient** means:
- If face auth succeeds → grant access immediately
- If face auth fails → try next method (password)

### Timeout Settings

Edit `pam/pam_face_auth.py`:
```python
timeout = 15  # Seconds to wait for face
```

### Enable/Disable for Specific Services

To add face auth to other services:
```bash
sudo nano /etc/pam.d/SERVICE_NAME

# Add before the password line:
auth    sufficient    pam_python.so pam_face_auth.py
```

Common services:
- `login` - Console login
- `su` - Switch user
- `polkit-1` - PolicyKit authentication
- `lightdm` - LightDM display manager
- `sddm` - SDDM display manager

---

## Troubleshooting

### Face Auth Not Triggering

Check syslog:
```bash
sudo tail -f /var/log/auth.log | grep face_auth
```

Common issues:
- Camera not accessible (check permissions)
- User not enrolled
- PAM module not found

### Locked Out

**Recovery methods:**

1. **Use password**: Face auth uses "sufficient", password still works
2. **Another user**: Login as different user
3. **SSH**: Remote login if enabled
4. **Recovery mode**: Boot into recovery, remove PAM config

### Remove Face Auth Quickly

```bash
# In emergency, remove the PAM lines
sudo sed -i '/pam_face_auth/d' /etc/pam.d/gdm-password
sudo sed -i '/pam_face_auth/d' /etc/pam.d/sudo
```

---

## Uninstallation

### Safe Uninstall

```bash
cd /path/to/linux-hello/pam
sudo ./uninstall_pam.sh
```

This will:
1. Remove PAM module
2. Clean PAM configuration
3. Restore password-only authentication

### Manual Uninstall

If script fails:
```bash
# Remove module
sudo rm /lib/security/pam_face_auth.py

# Remove from PAM configs
sudo sed -i '/pam_face_auth/d' /etc/pam.d/*

# Verify
grep -r "pam_face_auth" /etc/pam.d/
```

---

## Security Considerations

### Strengths
- Encrypted face data storage
- Password fallback always available
- Audit logging
- No network dependencies

### Limitations
- **Not as secure as password**: Face recognition can be fooled
- **Lighting dependent**: Poor lighting affects accuracy
- **No liveness detection**: Photos might work (unless enabled)
- **Single factor**: Consider using with password for critical systems

### Best Practices

1. **Use for convenience, not security**: Good for screen unlock, not for root access
2. **Keep password strong**: Face auth is supplementary
3. **Enable liveness detection**: Edit `config.yaml`:
   ```yaml
   security:
     require_liveness: true  # Experimental
   ```
4. **Monitor logs**: Check `/var/log/auth.log` regularly
5. **Update samples**: Re-enroll if appearance changes significantly

---

## Advanced Configuration

### Multiple Faces per User

Enroll multiple samples for better accuracy:
```bash
face-auth add-sample $USER
```

### Adjust Tolerance

Edit `config.yaml`:
```yaml
recognition:
  tolerance: 0.6  # Lower = stricter (0.4-0.7 recommended)
```

### Custom PAM Configuration

For more control, edit `/etc/pam.d/SERVICE`:

```
# Try face auth first (sufficient)
auth    sufficient    pam_python.so pam_face_auth.py

# Require password as backup (required)
auth    required      pam_unix.so

# Or make face auth required (no fallback - DANGEROUS!)
auth    required      pam_python.so pam_face_auth.py
```

---

## Testing Checklist

Before deploying to production:

- [ ] Face authentication works reliably in GUI
- [ ] Face authentication works in CLI
- [ ] Password fallback works
- [ ] Tested in virtual machine first
- [ ] Backup access method available
- [ ] Know how to boot into recovery mode
- [ ] Tested sudo authentication
- [ ] Tested screen unlock
- [ ] Tested system login
- [ ] Reviewed syslog output
- [ ] Uninstall script tested

---

## FAQ

**Q: Will I be locked out if face auth fails?**  
A: No, password fallback is always available.

**Q: Can I use this for root login?**  
A: Not recommended. Use for regular user accounts only.

**Q: Does this work over SSH?**  
A: No, requires local camera access.

**Q: Can I use multiple cameras?**  
A: Yes, configure in `config.yaml`.

**Q: What if my appearance changes?**  
A: Add new samples or re-enroll.

---

## Support

If you encounter issues:

1. Check syslog: `sudo tail -f /var/log/auth.log`
2. Test face auth in CLI: `face-auth test`
3. Verify camera works: `face-auth camera-test`
4. Check PAM config: `cat /etc/pam.d/gdm-password`
5. Restore from backup if needed

**Remember**: Always have a backup way to login!
