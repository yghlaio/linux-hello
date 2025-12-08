# Known Issues & Limitations

## ⚠️ Important Notice

This document lists all known bugs, limitations, and areas for improvement in the Face Authentication System. Please read this before deploying to production.

---

## Security Limitations

### 🔴 Critical - Not Password-Equivalent Security

**Issue:** Face recognition is fundamentally less secure than a strong password.

**Impact:**
- Can be fooled by high-quality photos
- Similar-looking people may authenticate
- Makeup, lighting, aging affect accuracy
- No cryptographic proof of identity

**Mitigation:**
- **NEVER use as sole authentication method**
- Always enable password fallback
- Use for convenience, not security
- Consider for screen unlock only, not for root/sudo

**Status:** By design - inherent limitation of biometric authentication

---

### 🟡 Medium - Liveness Detection Experimental

**Issue:** Basic liveness detection is experimental and may not prevent photo attacks.

**Impact:**
- Printed photos may work
- Screen photos may work
- 3D masks not tested

**Mitigation:**
- Enable liveness detection: `security.require_liveness: true`
- Use in conjunction with password
- Monitor authentication logs

**Status:** Experimental feature, needs improvement

---

## Hardware Limitations

### 🔴 Critical - No IR Camera Support

**Issue:** Unlike Howdy, this system does not support infrared cameras.

**Impact:**
- Poor performance in low light
- No depth sensing
- Less secure than IR-based systems
- Cannot detect 3D vs 2D faces

**Comparison with Howdy:**
- Howdy: Uses IR camera for better security and low-light
- This system: Standard RGB camera only

**Mitigation:**
- Ensure good lighting
- Use external lighting if needed
- Consider Howdy if you have IR camera

**Status:** No plans to add IR support (requires specialized hardware)

---

### 🟡 Medium - Camera Compatibility Issues

**Issue:** Some cameras may not work properly or at all.

**Known problematic cameras:**
- Some USB webcams with custom drivers
- Virtual cameras (OBS, v4l2loopback)
- Cameras requiring proprietary software

**Symptoms:**
- "Camera not found" error
- Black screen
- Frozen video
- Poor image quality

**Workaround:**
```bash
# Test camera first
./venv/bin/python3 utils/camera_test.py

# Try different device IDs
# Edit config.yaml
camera:
  device_id: "/dev/video1"  # Try video0, video1, video2, etc.
```

**Status:** Hardware-dependent, cannot fix all cases

---

### 🟢 Low - Performance Varies by Hardware

**Issue:** Recognition speed depends heavily on CPU/GPU.

**Typical performance:**
- Modern CPU (hog model): 1-3 seconds
- Older CPU (hog model): 3-10 seconds
- GPU (cnn model): 2-5 seconds
- Raspberry Pi: 5-15 seconds

**Impact:**
- Slow authentication on older hardware
- High CPU usage during recognition
- May timeout on very slow systems

**Mitigation:**
```yaml
# Use faster model
recognition:
  model: "hog"  # Faster than "cnn"
  
# Increase timeout
monitoring:
  check_interval: 5.0  # Slower checks = less CPU
```

**Status:** Hardware-dependent, optimize where possible

---

## Software Limitations

### 🟡 Medium - Python 3.14 Compatibility Issues

**Issue:** face_recognition library has compatibility issues with Python 3.14.

**Symptoms:**
- Import warnings about `pkg_resources`
- Deprecation warnings
- Potential future breakage

**Current workaround:**
- Pinned `setuptools<81` to avoid warnings
- May break in future Python versions

**Status:** Waiting for face_recognition library update

---

### 🟡 Medium - Large Memory Footprint

**Issue:** System uses significant memory, especially with many users.

**Memory usage:**
- Base: ~200MB
- Per user (5 samples): ~50MB
- With monitoring: +100MB
- Total for 10 users: ~800MB

**Impact:**
- May be problematic on low-RAM systems
- Monitoring daemon uses memory continuously

**Mitigation:**
- Limit number of enrolled users
- Reduce number of samples per user
- Don't run monitoring on low-RAM systems

**Status:** Inherent to face_recognition library

---

### 🟡 Medium - dlib Compilation Slow

**Issue:** First-time installation can take 10-30 minutes due to dlib compilation.

**Impact:**
- Long installation time
- High CPU usage during install
- May fail on systems without compiler

**Mitigation:**
- Be patient during installation
- Ensure build tools installed:
  ```bash
  sudo dnf install gcc-c++ cmake  # Fedora
  sudo apt install build-essential cmake  # Ubuntu
  ```

**Status:** Upstream dependency, cannot fix

---

## Functionality Limitations

### ✅ Fixed - Rotation Invariance Implemented

**Issue:** Face detection failed when face or device was rotated 90°, 180°, or 270°.

**Solution:** Implemented multi-angle detection and multi-angle enrollment wizard.

**Status:** ✅ Implemented and working

---

### PAM Integration

### ✅ Resolved - PAM Module Setup

**Status:** Migrated to `pam_exec.so` which is stable and reliable.

**Implementation:**
- Uses standard `pam_exec.so` module (no custom PAM modules needed)
- Runs `face-auth pam-authenticate` command 
- Privilege dropping implemented for seamless sudo usage
- Password fallback always available when face auth times out or fails

**Configuration Example:**
```
auth    sufficient    pam_exec.so quiet stdout /usr/local/bin/face-auth pam-authenticate
```

---

## Platform-Specific Issues
...
## Comparison with Howdy

### Features We're Missing

❌ **IR Camera Support** - Howdy's main advantage
❌ **Nod to Confirm** - Future feature
❌ **Mature Community** - Howdy has more users

### Features We Have

✅ **GUI Application** - Howdy only has CLI + GTK config
✅ **Multi-angle Enrollment** - Interactive wizard for robust face capture
✅ **Rotation Invariance** - Works at any angle
✅ **Sample Management** - More granular control
✅ **Bash Integration** - Easy script integration
✅ **Comprehensive Documentation** - More detailed guides
✅ **Event Hooks** - Custom script triggers  

---

## Workarounds & Tips

### Improve Accuracy

1. **Enroll in good lighting**
2. **Capture 10+ samples** instead of default 5
3. **Enroll with glasses on AND off**
4. **Add samples periodically**
5. **Use balanced or secure mode**

### Improve Performance

1. **Use hog model** (faster than cnn)
2. **Reduce num_jitters** to 1
3. **Increase check_interval** for monitoring
4. **Limit enrolled users**

### Improve Security

1. **Use secure mode**
2. **Enable liveness detection**
3. **Always have password fallback**
4. **Monitor auth logs regularly**
5. **Never use for root access**

---

## Reporting Issues

If you encounter a bug not listed here:

1. **Check logs:**
   ```bash
   tail -f ~/.local/share/face-auth/face_auth.log
   sudo tail -f /var/log/auth.log  # For PAM
   ```

2. **Test camera:**
   ```bash
   ./venv/bin/python3 utils/camera_test.py
   ```

3. **Validate config:**
   ```bash
   ./venv/bin/python3 cli.py validate-config
   ```

4. **Gather info:**
   ```bash
   ./venv/bin/python3 cli.py status
   python3 --version
   uname -a
   ```

5. **Open issue** with:
   - Description of problem
   - Steps to reproduce
   - Log output
   - System information

---

## Future Improvements

### Planned
- ✅ Multi-angle enrollment (completed)
- ✅ Security modes (implemented)
- ✅ PAM integration via pam_exec (stable)
- ⏳ Database locking
- ⏳ Better error messages
- ⏳ GUI improvements

### Under Consideration
- Automatic model updates
- Nod to confirm feature
- IR camera support (requires hardware)
- Mobile app integration
- Cloud backup (privacy concerns)

### Not Planned
- Windows/Mac support
- Remote authentication
- Fingerprint integration
- Voice recognition

---

## Disclaimer

This software is provided "as is" without warranty. Use at your own risk. The developers are not responsible for:

- System lockouts
- Security breaches
- Data loss
- Hardware damage
- Any other issues

**Always maintain alternative authentication methods!**
