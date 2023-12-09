# Wait for Network connection
sleep 5

cd git/animatronic/

# Check for updates
git fetch
git pull

# Run client script
python3 client.py

