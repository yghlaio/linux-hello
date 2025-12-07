#!/bin/bash
# PAM Face Authentication - Installation Script
# WARNING: This modifies system authentication. Use with caution!

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PAM_MODULE_DIR="/lib/security"
PAM_CONFIG_DIR="/etc/pam.d"

echo "========================================="
echo "Face Authentication PAM Installation"
echo "========================================="
echo
echo "⚠️  WARNING: This will modify system authentication!"
echo "⚠️  Make sure you have a backup and another way to login!"
echo
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Installation cancelled"
    exit 0
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    exit 1
fi

echo
echo "Step 1: Checking dependencies..."

# Check if python-pam is installed
if ! python3 -c "import pam" 2>/dev/null; then
    echo "❌ python-pam not installed"
    echo "Install with: pip install python-pam"
    exit 1
fi

echo "✅ Dependencies OK"

echo
echo "Step 2: Installing PAM module..."

# Copy PAM module
cp "$SCRIPT_DIR/pam_face_auth.py" "$PAM_MODULE_DIR/"
chmod 644 "$PAM_MODULE_DIR/pam_face_auth.py"

echo "✅ PAM module installed"

echo
echo "Step 3: Configuring PAM..."

# Backup existing PAM configuration
backup_dir="/etc/pam.d/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r "$PAM_CONFIG_DIR"/* "$backup_dir/"

echo "✅ PAM configuration backed up to $backup_dir"

# Configure for GDM (GNOME Display Manager)
if [ -f "$PAM_CONFIG_DIR/gdm-password" ]; then
    echo "Configuring GDM..."
    
    # Add face auth before password (sufficient means it will try face first)
    if ! grep -q "pam_face_auth" "$PAM_CONFIG_DIR/gdm-password"; then
        sed -i '/^auth.*pam_unix.so/i auth    sufficient    pam_python.so pam_face_auth.py' "$PAM_CONFIG_DIR/gdm-password"
        echo "✅ GDM configured"
    else
        echo "⚠️  GDM already configured"
    fi
fi

# Configure for sudo
if [ -f "$PAM_CONFIG_DIR/sudo" ]; then
    echo "Configuring sudo..."
    
    if ! grep -q "pam_face_auth" "$PAM_CONFIG_DIR/sudo"; then
        sed -i '/^auth.*pam_unix.so/i auth    sufficient    pam_python.so pam_face_auth.py' "$PAM_CONFIG_DIR/sudo"
        echo "✅ sudo configured"
    else
        echo "⚠️  sudo already configured"
    fi
fi

echo
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo
echo "IMPORTANT:"
echo "1. Test authentication in a NEW terminal session"
echo "2. Keep this terminal open as backup"
echo "3. If face auth fails, password will be used as fallback"
echo "4. To uninstall, run: ./uninstall_pam.sh"
echo
echo "Backup location: $backup_dir"
echo
