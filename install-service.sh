#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/rapha-ui.service"

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Error: rapha-ui.service not found in $SCRIPT_DIR"
  exit 1
fi

echo "Installing Rapha UI service..."
echo "Make sure you've edited rapha-ui.service with your username and paths first!"
echo ""

sudo cp "$SERVICE_FILE" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rapha-ui
sudo systemctl start rapha-ui
sudo systemctl status rapha-ui
