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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "Step 1: Installing Python dependencies..."
echo

# Check if virtual environment exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Using existing virtual environment"
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Install dependencies
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

echo
echo "✓ Python dependencies installed"

echo
echo "Step 2: Creating directories..."
echo

# Create necessary directories
mkdir -p "$HOME/.local/share/face-auth"
mkdir -p "$HOME/.config/face-auth"
mkdir -p "$SYSTEMD_DIR"

echo "✓ Directories created"

echo
echo "Step 3: Installing configuration..."
echo

# Copy default config if user config doesn't exist
if [ ! -f "$HOME/.config/face-auth/config.yaml" ]; then
    cp "$SCRIPT_DIR/config.yaml" "$HOME/.config/face-auth/config.yaml"
    echo "✓ Configuration file installed"
else
    echo "✓ Configuration file already exists (not overwriting)"
fi

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

# Create symlink for CLI
mkdir -p "$HOME/.local/bin"
ln -sf "$SCRIPT_DIR/cli.py" "$HOME/.local/bin/face-auth"

echo "✓ CLI symlink created at ~/.local/bin/face-auth"

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
