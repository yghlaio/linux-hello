#!/bin/bash
# Example: Simple authentication gate
# This script demonstrates basic face authentication

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../face-auth.sh"

echo "==================================="
echo "Face Authentication Gate"
echo "==================================="
echo

# Authenticate user
if face_auth 10; then
    echo "✅ Access granted!"
    echo "   User: $FACE_AUTH_USER"
    echo "   Confidence: $FACE_AUTH_CONFIDENCE"
    echo
    
    # Your protected script logic here
    echo "Running protected commands..."
    
    exit 0
else
    echo "❌ Access denied!"
    echo "   Authentication failed"
    exit 1
fi
