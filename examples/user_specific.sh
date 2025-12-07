#!/bin/bash
# Example: User-specific actions
# This script runs different commands based on who is authenticated

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../face-auth.sh"

echo "==================================="
echo "User-Specific Script Executor"
echo "==================================="
echo

# Authenticate user
if face_auth 15; then
    echo "✅ Authenticated as: $FACE_AUTH_USER"
    echo

    # Run user-specific commands
    case "$FACE_AUTH_USER" in
        alice)
            echo "Running Alice's configuration..."
            # Add Alice-specific commands here
            echo "  - Setting theme to dark mode"
            echo "  - Loading Alice's workspace"
            ;;
        bob)
            echo "Running Bob's configuration..."
            # Add Bob-specific commands here
            echo "  - Setting theme to light mode"
            echo "  - Loading Bob's workspace"
            ;;
        *)
            echo "Running default configuration for $FACE_AUTH_USER..."
            # Add default commands here
            ;;
    esac
    
    exit 0
else
    echo "❌ Authentication failed"
    exit 1
fi
