set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="vfetch"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  ██╗   ██╗███████╗███████╗████████╗ ██████╗██╗  ██╗"
echo "  ██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██║  ██║"
echo "  ██║   ██║█████╗  █████╗     ██║   ██║     ███████║"
echo "  ╚██╗ ██╔╝██╔══╝  ██╔══╝     ██║   ██║     ██╔══██║"
echo "   ╚████╔╝ ██║     ███████╗   ██║   ╚██████╗██║  ██║"
echo "    ╚═══╝  ╚═╝     ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝"
echo ""
echo "  Modern Animated System Info Tool"
echo "  ─────────────────────────────────"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "  [!] Python 3 is required but not found."
    echo "      Run: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  [✓] Python $PYTHON_VERSION found"

if ! python3 -m pip --version &>/dev/null 2>&1; then
    echo "  [~] pip not found, installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-pip python3-psutil 2>/dev/null || true
    fi
fi

echo "  [~] Installing Python dependencies..."

INSTALL_OPTS="--break-system-packages"
if python3 -c "import sys; sys.exit(0 if sys.prefix != sys.base_prefix else 1)" 2>/dev/null; then
    INSTALL_OPTS=""
fi

python3 -m pip install psutil rich $INSTALL_OPTS --quiet 2>/dev/null || {
    python3 -m pip install psutil rich --quiet 2>/dev/null || {
        if command -v apt-get &>/dev/null; then
            sudo apt-get install -y python3-psutil 2>/dev/null || true
        fi
        echo "  [!] Warning: Could not install all Python packages automatically."
        echo "      Try manually: pip install psutil rich"
    }
}

echo "  [✓] Dependencies installed"

echo "  [~] Installing vfetch to $INSTALL_DIR..."

if [[ ! -w "$INSTALL_DIR" ]]; then
    sudo install -m 755 "$REPO_DIR/vfetch.py" "$INSTALL_DIR/$SCRIPT_NAME"
else
    install -m 755 "$REPO_DIR/vfetch.py" "$INSTALL_DIR/$SCRIPT_NAME"
fi

PYTHON_PATH=$(command -v python3)
if [[ "$PYTHON_PATH" != "/usr/bin/env python3" ]]; then
    sudo sed -i "1s|.*|#!$PYTHON_PATH|" "$INSTALL_DIR/$SCRIPT_NAME" 2>/dev/null || true
fi

echo "  [✓] vfetch installed to $INSTALL_DIR/$SCRIPT_NAME"

CONFIG_DIR="$HOME/.config/vfetch"
CONFIG_FILE="$CONFIG_DIR/config.json"
mkdir -p "$CONFIG_DIR"

if [[ ! -f "$CONFIG_FILE" ]]; then
    cp "$REPO_DIR/config.example.json" "$CONFIG_FILE" 2>/dev/null || \
    python3 "$INSTALL_DIR/$SCRIPT_NAME" --init-config 2>/dev/null || true
    echo "  [✓] Default config written to $CONFIG_FILE"
else
    echo "  [~] Config already exists at $CONFIG_FILE (skipping)"
fi

echo ""
echo "  ┌──────────────────────────────────────┐"
echo "  │  vfetch installed successfully! 🎉    │"
echo "  │                                        │"
echo "  │  Run: vfetch                           │"
echo "  │  Themes: vfetch --list-themes          │"
echo "  │  Live:   vfetch --live                 │"
echo "  │  Config: ~/.config/vfetch/config.json  │"
echo "  └──────────────────────────────────────┘"
echo ""
