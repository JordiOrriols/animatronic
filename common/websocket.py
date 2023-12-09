

import asyncio
from websockets.sync.client import connect

from common.autodiscovery import AutoDiscovery
from common.logger import Logger
from common.config import WEBSOCKET_PORT, WEBSOCKET_MESSAGES

class WebSocketClient(Logger):
    def __init__(self):
        super().__init__('WebSocketClient')

        self.__continue_loop = True
        self.__websocket = None
        self.__autoDiscovery = AutoDiscovery()

    def connect(self):
        
        # Auto Discovery - UPD LISTENING
        self.info('Discovering servers...')

        current_ip = self.__autoDiscovery.listen()

        self.info('Server found at ', current_ip)
        self.info('Connecting...')

        loop = asyncio.get_event_loop()
        self.__websocket = loop.run_until_complete(self.__connect_websocket(current_ip))

        self.info("Connected successfully")
        self.send(WEBSOCKET_MESSAGES['connected'])

    async def __connect_websocket(self, current_ip):
        uri = "ws://" + current_ip + ":" + str(WEBSOCKET_PORT)
        return await connect(uri)
    
    def ready(self, handler):

        self.send(WEBSOCKET_MESSAGES['ready'])
        self.__continue_loop = True

        while self.__continue_loop:

            message = self.__websocket.recv()
            self.info(f"Message recieved: {message}")

            if message == WEBSOCKET_MESSAGES['exit']:
                self.__continue_loop = False
            
            handler(message)

    # Send
    # Send
    # Send

    def send(self, msg):
        if self.__websocket != None:
            self.__websocket.send(msg)
            self.info('Message sent', msg)
        else:
            self.error('Cannot send message', msg)