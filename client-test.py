import time

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

client = WebSocketClient()

# Start Websocket
client = WebSocketClient()
client.connect()

def handler(msg):
    if msg == WEBSOCKET_MESSAGES['play']:
        time.sleep(5)
        client.send(WEBSOCKET_MESSAGES['finished'])

client.ready(handler)