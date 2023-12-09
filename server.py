import asyncio
import threading
from time import sleep
from playsound import playsound

from websockets.server import serve
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname

from common.autodiscovery import DISCOVERY_PORT, DISCOVERY_MAGIC
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES

# Auto Discovery - UDP BROADCAST

socket_ip = socket(AF_INET, SOCK_DGRAM) # Create UDP socket

def get_local_ip():
    try:
        # Create a socket to get the local IP address
        socket_ip.connect(("8.8.8.8", 80))  # Connect to a known external server (Google's public DNS)
        local_ip = socket_ip.getsockname()[0]
        socket_ip.close()
        return local_ip
    except socket.error as e:
        print(f"Error getting local IP address: {e}")
        current_ip = gethostbyname(gethostname()) # get our IP. Be careful if you have multiple network interfaces or IPs
        return current_ip

# Example usage
current_ip = get_local_ip()
print("Local IP address:", current_ip)
auto_discovery = True

socket_broadcast = socket(AF_INET, SOCK_DGRAM) # Create UDP socket
socket_broadcast.bind(('', 0))
socket_broadcast.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # This is a broadcast socket

def sendAutoDiscovery():
    while True:
        if(auto_discovery == True):
            data = DISCOVERY_MAGIC + str(current_ip)
            socket_broadcast.sendto(str.encode(data), ('<broadcast>', DISCOVERY_PORT))
            print("AutoDiscovery - Sent service announcement", data)
            sleep(5)
        else:
            sleep(10)

thread = threading.Thread(target=sendAutoDiscovery)
thread.start()

# Websocket

print('Websocket Server Started')
print(' - Current IP', current_ip)
print(' - Websocket url', "ws://" + current_ip + ":" + str(WEBSOCKET_PORT))

async def handler(websocket):
    global auto_discovery
    
    async for message in websocket:

        print("Websocket Message: ", message)

        if message == WEBSOCKET_MESSAGES['connected']:
            auto_discovery = False

        if message == WEBSOCKET_MESSAGES['ready'] or message == WEBSOCKET_MESSAGES['finished']:
            await websocket.send(WEBSOCKET_MESSAGES['waiting'])
            input('Press any key to start')
            print("Playing Animation: ")
            await websocket.send(WEBSOCKET_MESSAGES['play'])
            sleep(1)
            playsound('sound/background.mp3', False)
            playsound('sound/laugh.mp3', False)

async def main():
    async with serve(handler, current_ip, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
