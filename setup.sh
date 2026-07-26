#!/bin/bash

echo "=== Installing Python dependencies ==="

pip install adafruit-circuitpython-servokit
pip install websockets
pip install python-dotenv
sudo apt install python3-smbus

# Ruta exacta de tu script de arranque
SCRIPT_PATH="$HOME/github/animatronic/startup.sh"
SERVICE_NAME="animatronic-startup.service"

echo "=== Configurando servicio para $SCRIPT_PATH ==="

# 1. Verificar si el script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "⚠️ Error: No se encuentra el archivo en $SCRIPT_PATH"
    echo "Por favor, comprueba que la ruta y el nombre del archivo sean correctos."
    exit 1
fi

# 2. Asegurar permisos de ejecución
chmod +x "$SCRIPT_PATH"
echo "✓ Permisos de ejecución aplicados a $SCRIPT_PATH"

# 3. Crear el servicio systemd
sudo bash -c "cat << SERVICE_EOF > /etc/systemd/system/$SERVICE_NAME
[Unit]
Description=Servicio de inicio Animatronic
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

# 4. Registrar y activar el servicio
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== ¡Listo! Estado actual del servicio: ==="
sudo systemctl status $SERVICE_NAME --no-pager

echo "=== Reiniciando ==="
sudo reboot