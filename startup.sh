# Wait for Network connection
sleep 5

# Check for updates
git fetch
git pull

# Run client script
python3 client.py