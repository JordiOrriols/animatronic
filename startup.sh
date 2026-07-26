#!/bin/bash

# If at some point you add this file to the startup of the raspberry pi
# This waits for Network connection
sleep 10

cd "$(dirname "$0")"

# Check for updates
git fetch
git pull

# Run client script
python3 client.py