#!/bin/bash
# Face Authentication System - Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: ./install.sh"
    exit 1
fi

# Activate venv and launch GUI
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 gui.py
