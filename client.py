import os
import json

from common.initialize import initialize, play

from common.websocket import WebSocketClient, messages

# Start Websocket
client = WebSocketClient()
client.connect()

initialize()

animation_name = 'animation'
with open('projects/' + os.getenv('PROJECT_ID') + '/' + animation_name + '.json') as json_file:

    data = json.load(json_file)

    def handler(msg):
        if msg == messages['play']:
            play(data)
            client.send(messages['finished'])

    client.ready(handler)