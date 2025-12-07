#!/bin/bash
# Example: Enrollment script
# This script helps enroll new users

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../face-auth.sh"

echo "==================================="
echo "Face Authentication - User Enrollment"
echo "==================================="
echo

# Get username
read -p "Enter username to enroll: " username

if [ -z "$username" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

# Check if already enrolled
if face_is_enrolled "$username"; then
    echo "⚠️  User '$username' is already enrolled"
    read -p "Do you want to remove and re-enroll? (y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        face_remove "$username"
    else
        exit 0
    fi
fi

# Get number of samples
read -p "Number of face samples (default: 5): " samples
samples="${samples:-5}"

echo
echo "Starting enrollment for '$username'..."
echo

# Enroll user
if face_enroll "$username" "$samples"; then
    echo
    echo "✅ Successfully enrolled $username!"
else
    echo
    echo "❌ Enrollment failed"
    exit 1
fi
