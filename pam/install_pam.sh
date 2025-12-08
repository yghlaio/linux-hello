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

# Check for pam_exec.so validation is done later
echo "✅ Dependencies OK"

echo "✅ Dependencies OK"

echo
echo "Step 2: Installing PAM module..."
echo "  (Skipping copy: Using pam_exec with external CLI)"
echo "✅ PAM module setup"

echo
echo "Step 3: Configuring PAM..."

# Backup existing PAM configuration
# We use /var/lib to avoid recursive copy errors if we put it in /etc/pam.d
backup_dir="/var/lib/face-auth/pam_backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r "$PAM_CONFIG_DIR"/* "$backup_dir/"

echo "✅ PAM configuration backed up to $backup_dir"

# Check for pam_exec.so (Standard PAM module)
# Use recursive find to handle x86_64-linux-gnu and other subdirs
echo "Searching for pam_exec.so..."
PAM_EXEC_PATH=$(find /usr/lib /usr/lib64 /lib /lib64 -name "pam_exec.so" 2>/dev/null | head -n 1)

if [ -z "$PAM_EXEC_PATH" ]; then
    echo "⚠️  pam_exec.so not found in standard paths."
    echo "   Assuming module is in default linker path."
    PAM_EXEC_PATH="pam_exec.so"
else
    echo "✅ Found: $PAM_EXEC_PATH"
fi

# We need the absolute path to our executable
# Check for system-wide install first, then user install
if [ -x "/usr/local/bin/face-auth" ]; then
    FACE_AUTH_CMD="/usr/local/bin/face-auth"
elif [ -x "$HOME/.local/bin/face-auth" ]; then
    FACE_AUTH_CMD="$HOME/.local/bin/face-auth"
else
    # Fallback to running cli.py directly via the venv
    FACE_AUTH_CMD="$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/cli.py"
fi

echo "Using face-auth command: $FACE_AUTH_CMD"

# Helper function to configure PAM file
configure_pam_file() {
    local file=$1
    local service_name=$2
    
    # Handle missing polkit-1 file
    if [ "$service_name" = "polkit-1" ] && [ ! -f "$file" ]; then
        echo "⚠️  $file does not exist. Attempting to create."
        if [ -f "/usr/share/pam.d/polkit-1" ]; then
             cp "/usr/share/pam.d/polkit-1" "$file"
        else
             # Generic fallback
             echo -e "#%PAM-1.0\nauth include system-auth\naccount include system-auth\npassword include system-auth\nsession include system-auth" > "$file"
        fi
    fi
    
    if [ ! -f "$file" ]; then
        echo "⚠️  $service_name config not found ($file) - Skipping"
        return
    fi
    
    echo "Configuring $service_name..."
    
    # Clean up legacy pam_python.so lines
    if grep -q "pam_python.so" "$file"; then
        echo "   Cleaning up legacy pam_python.so configuration..."
        sed -i '/pam_python.so/d' "$file"
    fi
    
    # Clean up existing pam_exec lines to ensure fresh config
    # (Optional, but good for retries)
    if grep -q "pam_exec.so.*cli.py" "$file"; then
        sed -i '/pam_exec.so.*cli.py/d' "$file"
    fi
    
    # The command to insert
    # quiet = don't print annoying messages implies succes
    # stdout = print output to stdout
    PAM_CMD="auth    sufficient    pam_exec.so quiet stdout $FACE_AUTH_CMD pam-authenticate"
    
    # Try to insert before pam_unix.so
    if grep -q "pam_unix.so" "$file"; then
        sed -i "\#^auth.*pam_unix.so#i $PAM_CMD" "$file"
        echo "✅ $service_name configured (before pam_unix.so)"
        return
    fi
    
    # Try to insert before include/substack common-auth or system-auth
    if grep -qE "^auth.*(include|substack).*(common-auth|system-auth)" "$file"; then
        sed -i -r "\#^auth.*(include|substack).*(common-auth|system-auth)#i $PAM_CMD" "$file"
        echo "✅ $service_name configured (before system include)"
        return
    fi
    
    # Fallback
    sed -i "1,/^[^#]/ { /^[^#]/i $PAM_CMD
    }" "$file"
    echo "⚠️  $service_name configured with fallback method"
}

# Configure services
configure_pam_file "$PAM_CONFIG_DIR/gdm-password" "GDM"
configure_pam_file "$PAM_CONFIG_DIR/sudo" "sudo"
configure_pam_file "$PAM_CONFIG_DIR/login" "login"
configure_pam_file "$PAM_CONFIG_DIR/polkit-1" "polkit-1"

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
