#!/bin/bash
# PAM Face Authentication - Uninstallation Script

set -e

PAM_MODULE_DIR="/lib/security"
PAM_CONFIG_DIR="/etc/pam.d"

echo "========================================="
echo "Face Authentication PAM Uninstallation"
echo "========================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    exit 1
fi

echo "Step 1: Removing PAM module..."

if [ -f "$PAM_MODULE_DIR/pam_face_auth.py" ]; then
    rm "$PAM_MODULE_DIR/pam_face_auth.py"
    echo "✅ PAM module removed"
else
    echo "⚠️  PAM module not found"
fi

echo
echo "Step 2: Removing PAM configuration..."

# Remove from GDM
if [ -f "$PAM_CONFIG_DIR/gdm-password" ]; then
    sed -i '/pam_exec.so.*face-auth/d' "$PAM_CONFIG_DIR/gdm-password"
    sed -i '/pam_exec.so.*cli.py.*pam-authenticate/d' "$PAM_CONFIG_DIR/gdm-password"
    sed -i '/pam_python.so.*pam_face_auth/d' "$PAM_CONFIG_DIR/gdm-password"
    echo "✅ GDM configuration cleaned"
fi

# Remove from sudo
if [ -f "$PAM_CONFIG_DIR/sudo" ]; then
    sed -i '/pam_exec.so.*face-auth/d' "$PAM_CONFIG_DIR/sudo"
    sed -i '/pam_exec.so.*cli.py.*pam-authenticate/d' "$PAM_CONFIG_DIR/sudo"
    sed -i '/pam_python.so.*pam_face_auth/d' "$PAM_CONFIG_DIR/sudo"
    echo "✅ sudo configuration cleaned"
fi

# Remove from polkit-1
if [ -f "$PAM_CONFIG_DIR/polkit-1" ]; then
    sed -i '/pam_exec.so.*face-auth/d' "$PAM_CONFIG_DIR/polkit-1"
    sed -i '/pam_exec.so.*cli.py.*pam-authenticate/d' "$PAM_CONFIG_DIR/polkit-1"
    sed -i '/pam_python.so.*pam_face_auth/d' "$PAM_CONFIG_DIR/polkit-1"
    echo "✅ polkit-1 configuration cleaned"
fi

# Remove from login
if [ -f "$PAM_CONFIG_DIR/login" ]; then
    sed -i '/pam_exec.so.*face-auth/d' "$PAM_CONFIG_DIR/login"
    sed -i '/pam_exec.so.*cli.py.*pam-authenticate/d' "$PAM_CONFIG_DIR/login"
    sed -i '/pam_python.so.*pam_face_auth/d' "$PAM_CONFIG_DIR/login"
    echo "✅ login configuration cleaned"
fi

echo
echo "========================================="
echo "✅ Uninstallation Complete!"
echo "========================================="
echo
echo "Face authentication has been removed from PAM"
echo "You can now login with password only"
echo
