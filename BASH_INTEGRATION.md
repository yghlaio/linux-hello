# Bash Integration Guide

## Quick Start

The face authentication system is now configured to use your camera at:
```
/dev/video0
```

## Using in Bash Scripts

### Method 1: Source the Library

```bash
#!/bin/bash
source /opt/linux-hello/face-auth.sh

# Authenticate user
if face_auth 10; then
    echo "Welcome $FACE_AUTH_USER"
    echo "Confidence: $FACE_AUTH_CONFIDENCE"
    # Your protected code here
else
    echo "Access denied"
    exit 1
fi
```

### Method 2: Direct CLI Usage

```bash
#!/bin/bash
cd /opt/linux-hello

# Authenticate
if ./venv/bin/python3 cli.py test --timeout 10 --no-preview; then
    echo "Authenticated!"
else
    echo "Failed"
    exit 1
fi
```

## Available Functions

When you source `face-auth.sh`, you get these functions:

### `face_auth [timeout]`
Authenticate user via face recognition
- **Returns**: 0 if authenticated, 1 if not
- **Sets**: `$FACE_AUTH_USER` and `$FACE_AUTH_CONFIDENCE`
- **Default timeout**: 10 seconds

```bash
if face_auth 15; then
    echo "User: $FACE_AUTH_USER"
    echo "Confidence: $FACE_AUTH_CONFIDENCE"
fi
```

### `face_is_enrolled <username>`
Check if a user is enrolled
- **Returns**: 0 if enrolled, 1 if not

```bash
if face_is_enrolled "alice"; then
    echo "Alice is enrolled"
fi
```

### `face_list_users`
List all enrolled users
- **Returns**: Usernames (one per line)

```bash
for user in $(face_list_users); do
    echo "Found user: $user"
done
```

### `face_enroll <username> [num_samples]`
Enroll a new user
- **Returns**: 0 if successful, 1 if failed
- **Default samples**: 5

```bash
face_enroll "alice" 5
```

### `face_remove <username>`
Remove an enrolled user
- **Returns**: 0 if successful, 1 if failed

```bash
face_remove "alice"
```

### `face_status`
Show system status

```bash
face_status
```

## Example Scripts

### Simple Authentication Gate

```bash
#!/bin/bash
source /path/to/face-auth.sh

if face_auth; then
    echo "✅ Access granted to $FACE_AUTH_USER"
    # Run protected commands
else
    echo "❌ Access denied"
    exit 1
fi
```

### User-Specific Actions

```bash
#!/bin/bash
source /path/to/face-auth.sh

if face_auth 15; then
    case "$FACE_AUTH_USER" in
        alice)
            echo "Running Alice's script..."
            ;;
        bob)
            echo "Running Bob's script..."
            ;;
        *)
            echo "Unknown user: $FACE_AUTH_USER"
            ;;
    esac
fi
```

### Conditional Access

```bash
#!/bin/bash
source /path/to/face-auth.sh

# Only allow specific users
ALLOWED_USERS=("alice" "bob")

if face_auth; then
    if [[ " ${ALLOWED_USERS[@]} " =~ " ${FACE_AUTH_USER} " ]]; then
        echo "✅ Access granted to $FACE_AUTH_USER"
    else
        echo "❌ User $FACE_AUTH_USER not authorized"
        exit 1
    fi
else
    echo "❌ Authentication failed"
    exit 1
fi
```

## Example Scripts Included

Pre-built example scripts are available in the `examples/` directory:

1. **[auth_gate.sh](file:///opt/linux-hello/examples/auth_gate.sh)**
   - Simple authentication gate
   - Demonstrates basic usage

2. **[user_specific.sh](file:///opt/linux-hello/examples/user_specific.sh)**
   - User-specific actions
   - Shows how to run different commands per user

3. **[enroll_user.sh](file:///opt/linux-hello/examples/enroll_user.sh)**
   - Interactive enrollment script
   - Easy way to enroll new users

Run them:
```bash
cd /opt/linux-hello
./examples/auth_gate.sh
./examples/user_specific.sh
./examples/enroll_user.sh
```

## Integration Patterns

### Cron Jobs

```bash
# In your crontab
0 9 * * * source /path/to/face-auth.sh && face_auth && /path/to/morning-routine.sh
```

### SSH Login Hook

Add to `~/.bashrc` or `~/.bash_profile`:
```bash
# Require face auth on login (optional)
if [ -n "$SSH_CONNECTION" ]; then
    source /path/to/face-auth.sh
    if ! face_auth 20; then
        echo "Face authentication required"
        exit 1
    fi
fi
```

### Script Protection

```bash
#!/bin/bash
# Protected script

source /path/to/face-auth.sh

# Require authentication
face_auth || exit 1

# Your sensitive commands here
echo "Running as $FACE_AUTH_USER..."
```

## Configuration

The system is configured to use your camera:
- **Device**: `/dev/video0`
- **Config file**: `config.yaml`
- **Database**: `~/.local/share/face-auth/face_auth.db` (created on first use)
- **Logs**: `~/.local/share/face-auth/face_auth.log` (created on first use)

To change settings, edit `config.yaml` in this directory.

## First-Time Setup

Before using in scripts, you need to:

1. **Install dependencies** (if not already done):
   ```bash
   cd /opt/linux-hello
   ./install.sh
   ```

2. **Enroll yourself**:
   ```bash
   ./examples/enroll_user.sh
   # OR
   source face-auth.sh
   face_enroll "$USER" 5
   ```

3. **Test authentication**:
   ```bash
   source face-auth.sh
   face_auth
   ```

## Troubleshooting

### Camera not found
```bash
# Check if camera is accessible
ls -l /dev/video0

# Test with OpenCV
source venv/bin/activate
python3 -c "import cv2; cap = cv2.VideoCapture('/dev/video0'); print('OK' if cap.isOpened() else 'FAIL')"
```

### No users enrolled
```bash
# List enrolled users
source face-auth.sh
face_list_users

# Enroll yourself
face_enroll "$USER"
```

### Authentication too strict/lenient
Edit `config.yaml`:
```yaml
recognition:
  tolerance: 0.6  # Lower = stricter (0.0-1.0)
```

## Notes

- All operations stay within `/opt/linux-hello`
- No system files are modified
- Database and logs are created in `~/.local/share/face-auth/` on first use
- No PAM integration - purely script-based
- Safe to use in automated scripts
