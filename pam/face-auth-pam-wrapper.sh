#!/bin/bash
# Async wrapper for face-auth PAM authentication
# This script runs face-auth in background and monitors for success
# allowing password entry to work in parallel

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULT_FILE="/tmp/face-auth-result-$$"
TIMEOUT=8

# Get PAM user
PAM_USER="${PAM_USER:-}"
if [ -z "$PAM_USER" ]; then
    echo "Face Auth: No PAM_USER set"
    exit 1
fi

# Find face-auth command
if [ -x "/usr/local/bin/face-auth" ]; then
    FACE_AUTH_CMD="/usr/local/bin/face-auth"
elif [ -x "/opt/linux-hello/venv/bin/python3" ]; then
    FACE_AUTH_CMD="/opt/linux-hello/venv/bin/python3 /opt/linux-hello/cli.py"
else
    echo "Face Auth: Command not found"
    exit 1
fi

# Run face-auth in background
(
    $FACE_AUTH_CMD pam-authenticate "$PAM_USER" > /dev/null 2>&1
    echo $? > "$RESULT_FILE"
) &
BG_PID=$!

# Wait for result with timeout, but exit quickly to allow password entry
# The key insight: we exit with failure immediately so PAM continues to password
# But if face-auth succeeds quickly, we catch it

START_TIME=$(date +%s)
while true; do
    # Check if result file exists (face-auth completed)
    if [ -f "$RESULT_FILE" ]; then
        RESULT=$(cat "$RESULT_FILE")
        rm -f "$RESULT_FILE"
        
        if [ "$RESULT" = "0" ]; then
            echo "Face Auth: Success!"
            exit 0
        else
            echo "Face Auth: Failed"
            exit 1
        fi
    fi
    
    # Check timeout (short - just 2 seconds to allow quick success)
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -ge 2 ]; then
        # Timeout - let password auth proceed, but keep face-auth running
        # It will complete in background (success won't help now though)
        echo "Face Auth: Checking... (use password if needed)"
        exit 1
    fi
    
    sleep 0.1
done
