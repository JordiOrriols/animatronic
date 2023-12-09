import asyncio
import threading
from time import sleep

from websockets.server import serve
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from playsound import playsound

from common.autodiscovery import DISCOVERY_PORT, DISCOVERY_MAGIC, WEBSOCKET_PORT, messages

# Init

current_ip = gethostbyname(gethostname()) # get our IP. Be careful if you have multiple network interfaces or IPs
auto_discovery = True

# Auto Discovery - UDP BROADCAST

s = socket(AF_INET, SOCK_DGRAM) # Create UDP socket
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # This is a broadcast socket

def sendAutoDiscovery():
    while True:
        if(auto_discovery == True):
            data = DISCOVERY_MAGIC + str(current_ip)
            s.sendto(str.encode(data), ('<broadcast>', DISCOVERY_PORT))
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

        if message == messages['connected']:
            auto_discovery = False

        if message == messages['ready'] or message == messages['finished']:
            await websocket.send(messages['waiting'])
            input('Press any key to start')
            await websocket.send(messages['play'])
            playsound('sound/background.mp3', False)
            playsound('sound/laugh.mp3', False)

async def main():
    async with serve(handler, current_ip, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
