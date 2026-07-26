#!/bin/bash

# If at some point you add this file to the startup of the raspberry pi
# This waits for Network connection

echo "=== Waiting for Internet connection... ==="
# Wait until we can ping 8.8.8.8 (maximum 30 attempts)
count=0
while ! ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; do
    echo "No network yet, waiting 2 seconds... ($count/30)"
    sleep 2
    count=$((count+1))
    if [ $count -ge 30 ]; then
        echo "⚠️ Timed out waiting for an Internet connection."
        break
    fi
done

echo "✓ Internet connection detected. Continuing startup..."

# --- Your current startup.sh code (git pull, python, etc.) ---

# cd "$(dirname "$0")"
echo "=== Moving to project directory... ==="
cd github/animatronic/

# Check for updates (optional: a failed fetch/pull should not block startup,
# e.g. if the network drops or the remote is unreachable)
echo "=== Checking for updates... ==="
if git fetch && git pull; then
    echo "✓ Repository updated successfully."
else
    echo "⚠️ Could not update repository (offline or git error?). Continuing with current code..."
fi

# Run client script
echo "=== Starting client... ==="
python3 client.py