#!/bin/bash

# If at some point you add this file to the startup of the raspberry pi
# This waits for Network connection
sleep 5

cd "$(dirname "$0")"

# Always boot from the main branch (self-heals if a previous calibration
# session was ever interrupted before switching back)
git checkout main

# Check for updates
git fetch
git pull

# Run client script
python3 client.py