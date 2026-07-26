#!/bin/bash

echo "=== Setting Git Config ==="
git config --global user.email "animatronic@jordiorriols.cat"
git config --global user.name "jordiorriols"

echo "=== Installing System & Python dependencies ==="
# Usamos apt para paquetes del sistema y la bandera --break-system-packages para pip global si es necesario
sudo apt update
sudo apt install -y python3-smbus python3-pip python3-websockets python3-dotenv

# Para librerías específicas que no están en apt (como adafruit-circuitpython-servokit)
pip install adafruit-circuitpython-servokit --break-system-packages --quiet

# Rutas exactas
SCRIPT_PATH="$HOME/github/animatronic/startup.sh"
SERVICE_NAME="animatronic-startup.service"

echo "=== Configuring service for $SCRIPT_PATH ==="

# 1. Verificar si el script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "⚠️ Error: File not found at $SCRIPT_PATH"
    echo "Please check that the path and file name are correct."
    exit 1
fi

# 2. Asegurar permisos de ejecución
chmod +x "$SCRIPT_PATH"
echo "✓ Execution permissions applied to $SCRIPT_PATH"

# 3. Crear el servicio systemd con /bin/bash y espera a red online
sudo bash -c "cat << SERVICE_EOF > /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=Animatronic startup service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/github/animatronic
ExecStart=/bin/bash $SCRIPT_PATH
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
SERVICE_EOF"

# 4. Registrar y activar el servicio
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== Done! Current service status: ==="
sudo systemctl status $SERVICE_NAME --no-pager

echo "=== Rebooting in 5 seconds... ==="
sleep 5
sudo reboot