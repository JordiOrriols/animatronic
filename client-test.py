import time

from websockets.sync.client import connect
from socket import socket, AF_INET, SOCK_DGRAM

from common.socket import DISCOVERY_PORT, DISCOVERY_MAGIC, WEBSOCKET_PORT, messages

# Auto Discovery - UPD LISTENING

s = socket(AF_INET, SOCK_DGRAM) # create UDP socket
s.bind(('', DISCOVERY_PORT))

current_ip = None

print("AutoDiscovery - Listening for service")

while current_ip == None:
    
    data, addr = s.recvfrom(1024) # wait for a packet
    print("AutoDiscovery - Data", data)

    if data.startswith(str.encode(DISCOVERY_MAGIC)):
        print("AutoDiscovery - Found service", data)
        current_ip = data[len(DISCOVERY_MAGIC):].decode('utf-8')
        print("AutoDiscovery - Current IP", current_ip)

# Start Websocket

print("Websocket - Connecting...")

with connect("ws://" + current_ip + ":" + str(WEBSOCKET_PORT)) as websocket:

    print("Websocket - Connected Successfully")
    websocket.send(messages['connected'])

    websocket.send(messages['ready'])
    continue_loop = True

    while continue_loop:

        message = websocket.recv()
        print(f"Websocket Event: {message}")

        if message == messages['play']:
            time.sleep(5)
            websocket.send(messages['finished'])
        elif message == messages['exit']:
            continue_loop = False