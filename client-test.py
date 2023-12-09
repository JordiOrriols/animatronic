import time

from common.websocket import WebSocketClient, messages

client = WebSocketClient()

# Start Websocket
client = WebSocketClient()
client.connect()


def handler(msg):
    if msg == messages['play']:
        time.sleep(5)
        client.send(messages['finished'])

client.ready(handler)