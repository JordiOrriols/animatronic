from common.project import Project

from common.websocket import WebSocketClient, messages

# Start Websocket
client = WebSocketClient()
client.connect()

project = Project()
project.load_animation('animation')

def handler(msg):
    if msg == messages['play']:
        project.play()
        client.send(messages['finished'])

client.ready(handler)