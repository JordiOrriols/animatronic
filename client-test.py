import time
import asyncio

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

# Start Websocket
client = WebSocketClient()
client.connect()


def handler(msg):
    if msg == WEBSOCKET_MESSAGES["play"]:
        time.sleep(5)
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif msg == WEBSOCKET_MESSAGES["auto"]:
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif msg == WEBSOCKET_MESSAGES["stop"]:
        client.send(WEBSOCKET_MESSAGES["finished"])


asyncio.run(client.ready(handler))
