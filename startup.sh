# If at some point you add this file to the startup of the raspberry pi
# This waits for Network connection
sleep 5

cd git/animatronic/

# Check for updates
git fetch
git pull

# Run client script
python3 client.py

