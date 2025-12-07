# Bash Integration - Quick Reference

## ✅ Configuration Complete

**Camera Device:** `/dev/video0`  
**Status:** Ready for bash script integration  
**PAM Integration:** Not configured (script-based only)

---

## 🚀 Quick Start

### 1. First-Time Setup

```bash
cd /path/to/linux-hello

# Install dependencies (if not done)
./install.sh

# Enroll yourself
./examples/enroll_user.sh
```

### 2. Use in Your Scripts

```bash
#!/bin/bash
source /path/to/linux-hello/face-auth.sh

if face_auth 10; then
    echo "✅ Welcome $FACE_AUTH_USER!"
    # Your protected commands
else
    echo "❌ Access denied"
    exit 1
fi
```

---

## 📚 Available Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `face_auth [timeout]` | Authenticate user | 0=success, 1=fail |
| `face_is_enrolled <user>` | Check enrollment | 0=enrolled, 1=not |
| `face_list_users` | List users | Usernames |
| `face_enroll <user> [samples]` | Enroll user | 0=success, 1=fail |
| `face_remove <user>` | Remove user | 0=success, 1=fail |
| `face_status` | System status | Status info |

---

## 📝 Example Scripts

All scripts are in `/path/to/linux-hello/examples/`:

1. **`auth_gate.sh`** - Simple authentication gate
2. **`user_specific.sh`** - User-specific actions
3. **`enroll_user.sh`** - Interactive enrollment

---

## 📖 Full Documentation

- **[BASH_INTEGRATION.md](file:///path/to/linux-hello/BASH_INTEGRATION.md)** - Complete guide with examples
- **[README.md](file:///path/to/linux-hello/README.md)** - System overview
- **[face-auth.sh](file:///path/to/linux-hello/face-auth.sh)** - Bash library source

---

## 🔧 Files Modified

Within `/path/to/linux-hello/` only:

- ✅ `config.yaml` - Updated camera device path
- ✅ `face-auth.sh` - NEW: Bash library
- ✅ `examples/auth_gate.sh` - NEW: Example script
- ✅ `examples/user_specific.sh` - NEW: Example script  
- ✅ `examples/enroll_user.sh` - NEW: Example script
- ✅ `BASH_INTEGRATION.md` - NEW: Documentation
- ✅ `README.md` - Updated with bash integration info

**No system files modified** ✓

---

## ⚡ Common Use Cases

### Protect a Script
```bash
source /path/to/face-auth.sh
face_auth || exit 1
# Protected commands here
```

### User-Specific Logic
```bash
source /path/to/face-auth.sh
if face_auth; then
    case "$FACE_AUTH_USER" in
        alice) run_alice_script ;;
        bob) run_bob_script ;;
    esac
fi
```

### Check Before Running
```bash
source /path/to/face-auth.sh
if face_is_enrolled "$USER"; then
    face_auth && run_protected_task
fi
```

---

## 🎯 Next Steps

1. **Enroll yourself**: `./examples/enroll_user.sh`
2. **Test authentication**: `source face-auth.sh && face_auth`
3. **Use in your scripts**: See examples above
4. **Read full guide**: [BASH_INTEGRATION.md](file:///path/to/linux-hello/BASH_INTEGRATION.md)
