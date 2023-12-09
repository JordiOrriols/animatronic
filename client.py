from common.project import Project

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

# Start Websocket
client = WebSocketClient()
client.connect()

project = Project()
project.load_animation('animation')

def handler(msg):
    if msg == WEBSOCKET_MESSAGES['play']:
        project.play()
        client.send(WEBSOCKET_MESSAGES['finished'])

client.ready(handler)