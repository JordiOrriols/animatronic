"""Websocket module to handle Websocket connection as a client."""

import json
from websockets.sync.client import connect

from common.autodiscovery import AutoDiscoveryClient
from common.logger import Logger
from common.config import WEBSOCKET_PORT, WEBSOCKET_MESSAGES


class WebSocketClient(Logger):
    """Class to handle Websocket connection as a client."""

    def __init__(self):
        super().__init__("WebSocketClient")

        self.__continue_loop = True
        self.__websocket = None
        self.__auto_discovery = AutoDiscoveryClient()

    def connect(self):
        """Wait until any server is found on AutoDiscovery via UDP Broadcast and connect."""
        # Auto Discovery - UPD LISTENING
        self.info("Discovering servers...")

        current_ip = self.__auto_discovery.listen()

        self.info("Server found at ", current_ip)
        self.info("Connecting...")

        uri = "ws://" + current_ip + ":" + str(WEBSOCKET_PORT)
        self.__websocket = connect(uri)

        self.info("Connected successfully")
        self.send(WEBSOCKET_MESSAGES["connected"])

    async def ready(self, handler):
        """Tell server client is ready to receive and process messages."""
        self.send(WEBSOCKET_MESSAGES["ready"])
        self.__continue_loop = True

        while self.__continue_loop:
            message = self.__websocket.recv()
            self.info(f"Message received: {message}")

            if message == WEBSOCKET_MESSAGES["exit"]:
                self.__continue_loop = False
                await self.__websocket.close()

            handler(message)

    # Send
    # Send
    # Send

    def send(self, action: str, *data):
        """Send message to the server."""
        if self.__websocket is not None:
            msg = json.dumps({action, data})
            self.__websocket.send(msg)
            self.info("Message sent", msg)
        else:
            self.error("Cannot send message", msg)
