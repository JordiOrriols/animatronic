#!/bin/bash

echo "=== Installing Python dependencies ==="

pip install adafruit-circuitpython-servokit
pip install websockets
pip install python-dotenv
sudo apt install python3-smbus

# Exact path to your startup script
SCRIPT_PATH="$HOME/github/animatronic/startup.sh"
SERVICE_NAME="animatronic-startup.service"

echo "=== Configuring service for $SCRIPT_PATH ==="

# 1. Check if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "⚠️ Error: File not found at $SCRIPT_PATH"
    echo "Please check that the path and file name are correct."
    exit 1
fi

# 2. Ensure execution permissions
chmod +x "$SCRIPT_PATH"
echo "✓ Execution permissions applied to $SCRIPT_PATH"

# 3. Create the systemd service
sudo bash -c "cat << SERVICE_EOF > /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=Animatronic startup service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/github/animatronic
ExecStart=$SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE_EOF"

# 4. Register and enable the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== Done! Current service status: ==="
sudo systemctl status $SERVICE_NAME --no-pager

echo "=== Rebooting ==="
sudo reboot