#!/usr/bin/env bash
# setup.sh — Run once on the Pi to install and enable mars-pi.
# Usage:  bash setup.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="mars-pi"

echo "=== mars-pi setup ==="
echo "Repo dir: $REPO_DIR"
echo ""

# ---------------------------------------------------------------------------
# 1. Enable camera interface (Raspberry Pi OS)
# ---------------------------------------------------------------------------
echo "[1/5] Enabling camera interface..."
if command -v raspi-config &>/dev/null; then
  sudo raspi-config nonint do_camera 0
  echo "      Camera interface enabled."
else
  echo "      raspi-config not found — skipping (non-Raspberry Pi OS detected)."
fi

# ---------------------------------------------------------------------------
# 2. System packages
# ---------------------------------------------------------------------------
echo "[2/5] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
  python3-pip \
  python3-venv \
  python3-picamera2 \
  libcamera-apps
echo "      System packages installed."

# ---------------------------------------------------------------------------
# 3. Python virtual environment
# ---------------------------------------------------------------------------
echo "[3/5] Creating Python virtual environment..."
python3 -m venv --system-site-packages "$REPO_DIR/venv"
"$REPO_DIR/venv/bin/pip" install --quiet --upgrade pip
"$REPO_DIR/venv/bin/pip" install --quiet -r "$REPO_DIR/requirements.txt"
echo "      Virtual environment ready at $REPO_DIR/venv"

# ---------------------------------------------------------------------------
# 4. systemd service
# ---------------------------------------------------------------------------
echo "[4/5] Installing systemd service..."
# Patch the service file with the actual repo path and current user
SERVICE_FILE="$REPO_DIR/$SERVICE_NAME.service"
CURRENT_USER="$(whoami)"

sed \
  -e "s|/home/pi/mars-pi|$REPO_DIR|g" \
  -e "s|User=pi|User=$CURRENT_USER|g" \
  "$SERVICE_FILE" | sudo tee "/etc/systemd/system/$SERVICE_NAME.service" > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
echo "      Service installed and enabled."

# ---------------------------------------------------------------------------
# 5. Start the service
# ---------------------------------------------------------------------------
echo "[5/5] Starting $SERVICE_NAME service..."
sudo systemctl restart "$SERVICE_NAME"
sleep 2
sudo systemctl status "$SERVICE_NAME" --no-pager || true

echo ""
echo "=== Setup complete ==="
echo "Stream URL : http://$(hostname -I | awk '{print $1}'):8000/stream"
echo "Health URL : http://$(hostname -I | awk '{print $1}'):8000/health"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo "  sudo systemctl restart $SERVICE_NAME"

