#!/bin/bash
# Installation script for Face Authentication System

set -e

echo "=========================================="
echo "Face Authentication System - Installation"
echo "=========================================="
echo

# Check if running as root for system-wide installation
if [ "$EUID" -eq 0 ]; then
    INSTALL_MODE="system"
    SYSTEMD_DIR="/etc/systemd/system"
    echo "Installing system-wide..."
else
    INSTALL_MODE="user"
    SYSTEMD_DIR="$HOME/.config/systemd/user"
    echo "Installing for current user..."
fi

# Get script directory
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/linux-hello"

# For system install, copy to /opt if not already there
if [ "$INSTALL_MODE" = "system" ] && [ "$SOURCE_DIR" != "$INSTALL_DIR" ]; then
    echo
    echo "📦 Relocating to $INSTALL_DIR for system-wide access..."
    
    # Create /opt/linux-hello if needed
    mkdir -p "$INSTALL_DIR"
    
    # Copy all files (excluding venv which will be recreated)
    rsync -a --exclude='venv' --exclude='.git' --exclude='__pycache__' \
          --exclude='*.pyc' --exclude='.cache' "$SOURCE_DIR/" "$INSTALL_DIR/"
    
    echo "✓ Copied to $INSTALL_DIR"
    
    # Use the new location
    SCRIPT_DIR="$INSTALL_DIR"
else
    SCRIPT_DIR="$SOURCE_DIR"
fi

echo
echo "Step 1: Installing system dependencies..."
echo

# Install required system libraries
install_system_deps() {
    if [ "$INSTALL_MODE" != "system" ]; then
        echo "⚠️  System dependencies require root. Please run with sudo if packages are missing."
    fi
    
    # Detect package manager and install dependencies
    if command -v dnf &> /dev/null; then
        echo "Detected Fedora/RHEL - using dnf"
        if [ "$INSTALL_MODE" = "system" ]; then
            dnf install -y openblas openblas-devel blas blas-devel lapack lapack-devel \
                cmake gcc gcc-c++ python3-devel \
                libX11-devel gtk3-devel || echo "⚠️  Some packages may have failed to install"
        else
            echo "Required packages: openblas openblas-devel blas blas-devel lapack lapack-devel cmake gcc gcc-c++ python3-devel"
            echo "Install manually: sudo dnf install openblas openblas-devel blas blas-devel lapack lapack-devel cmake gcc gcc-c++ python3-devel"
        fi
    elif command -v apt-get &> /dev/null; then
        echo "Detected Debian/Ubuntu - using apt"
        if [ "$INSTALL_MODE" = "system" ]; then
            apt-get update
            apt-get install -y libopenblas-dev cmake build-essential python3-dev \
                libx11-dev libgtk-3-dev || echo "⚠️  Some packages may have failed to install"
        else
            echo "Required packages: libopenblas-dev cmake build-essential python3-dev"
            echo "Install manually: sudo apt install libopenblas-dev cmake build-essential python3-dev"
        fi
    elif command -v pacman &> /dev/null; then
        echo "Detected Arch Linux - using pacman"
        if [ "$INSTALL_MODE" = "system" ]; then
            pacman -Sy --noconfirm openblas cmake gcc python || echo "⚠️  Some packages may have failed to install"
        else
            echo "Required packages: openblas cmake gcc python"
            echo "Install manually: sudo pacman -S openblas cmake gcc python"
        fi
    else
        echo "⚠️  Unknown package manager. Please ensure these libraries are installed:"
        echo "   - OpenBLAS (libopenblas.so)"
        echo "   - CMake"
        echo "   - GCC/G++"
        echo "   - Python development headers"
    fi
}

# Check if libopenblas is available
if ! ldconfig -p 2>/dev/null | grep -q libopenblas || ! command -v cmake &> /dev/null; then
    echo "Installing required system dependencies..."
    install_system_deps
else
    echo "✓ System dependencies already installed"
fi

echo
echo "Step 2: Installing Python dependencies..."
echo

# Check if virtual environment exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Using existing virtual environment"
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "Creating virtual environment..."
    # Use --copies to avoid symlink issues on shared folders (VMs)
    python3 -m venv --copies "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Install dependencies
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

echo
echo "✓ Python dependencies installed"

echo
echo "Step 3: Setting permissions for PAM/GDM access..."
echo

# Make venv accessible to all users (required for GDM/PAM)
if [ "$INSTALL_MODE" = "system" ]; then
    echo "Setting world-readable permissions for venv..."
    chmod -R o+rX "$SCRIPT_DIR/venv"
    chmod o+rx "$SCRIPT_DIR"
    chmod o+r "$SCRIPT_DIR"/*.py
    echo "✓ Permissions set for GDM/PAM access"
else
    echo "⚠️  User-mode install: GDM/PAM may not work without sudo ./install.sh"
fi

echo
echo "Step 4: Configuring system..."
echo

# Directory creation is handled by the application at runtime
# to ensure correct ownership.


echo
echo "Step 4: Installing systemd services..."
echo

# Define service file paths
SERVICE_FILE="$SYSTEMD_DIR/face-auth-monitor.service"
DBUS_SERVICE_FILE="$SYSTEMD_DIR/face-auth-dbus.service"

# Get current user
CURRENT_USER=$(whoami)
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"

# Create systemd service from template with variable substitution
echo "Creating monitor service for user: $CURRENT_USER"
sed -e "s|{{PYTHON_PATH}}|$PYTHON_PATH|g" \
    -e "s|{{PROJECT_DIR}}|$SCRIPT_DIR|g" \
    -e "s|{{USER}}|$CURRENT_USER|g" \
    "$SCRIPT_DIR/systemd/face-auth-monitor.service.template" > "$SERVICE_FILE"

echo "Creating D-Bus service for user: $CURRENT_USER"
sed -e "s|{{PYTHON_PATH}}|$PYTHON_PATH|g" \
    -e "s|{{PROJECT_DIR}}|$SCRIPT_DIR|g" \
    -e "s|{{USER}}|$CURRENT_USER|g" \
    "$SCRIPT_DIR/systemd/face-auth-dbus.service.template" > "$DBUS_SERVICE_FILE"

# Reload systemd
if [ "$INSTALL_MODE" = "system" ]; then
    systemctl daemon-reload
else
    systemctl --user daemon-reload
fi

echo "✓ Systemd services installed"

echo
echo "Step 5: Making scripts executable..."
echo

chmod +x "$SCRIPT_DIR/cli.py"
chmod +x "$SCRIPT_DIR/monitor_daemon.py"
chmod +x "$SCRIPT_DIR/dbus_service.py"
chmod +x "$SCRIPT_DIR/examples/"*.sh

echo "✓ Scripts are executable"

echo
echo "Step 6: Creating CLI symlink..."
echo

# Create launcher script
if [ "$INSTALL_MODE" = "system" ]; then
    LAUNCHER_DIR="/usr/local/bin"
else
    mkdir -p "$HOME/.local/bin"
    LAUNCHER_DIR="$HOME/.local/bin"
fi

LAUNCHER="$LAUNCHER_DIR/face-auth"

cat > "$LAUNCHER" << EOF
#!/bin/bash
exec "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/cli.py" "\$@"
EOF

chmod +x "$LAUNCHER"

echo "✓ CLI launcher created at $LAUNCHER"

echo
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Ensure ~/.local/bin is in your PATH:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
echo
echo "2. Enroll your face:"
echo "   face-auth enroll"
echo
echo "3. Test authentication:"
echo "   face-auth test"
echo
echo "4. Start monitoring daemon:"
if [ "$INSTALL_MODE" = "system" ]; then
    echo "   sudo systemctl enable --now face-auth-monitor.service"
else
    echo "   systemctl --user enable --now face-auth-monitor.service"
fi
echo
echo "5. (Optional) Start D-Bus service:"
if [ "$INSTALL_MODE" = "system" ]; then
    echo "   sudo systemctl enable --now face-auth-dbus.service"
else
    echo "   systemctl --user enable --now face-auth-dbus.service"
fi
echo
echo "For more information, see README.md"
echo
