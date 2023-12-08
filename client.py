import os
import json
from websockets.sync.client import connect
from common.initialize import initialize, play
from common.socket import url, port, messages

with connect("ws://" + url + ":" + str(port)) as websocket:

    websocket.send(messages['connected'])
    
    initialize()

    animation_name = 'animation'
    with open(os.getenv('PROJECT_ID') + '/' + animation_name + '.json') as json_file:
    
        data = json.load(json_file)
        websocket.send(messages['ready'])
        continue_loop = True

        while continue_loop:

            message = websocket.recv()
            print(f"Socket Event: {message}")

            if message == messages['play']:
                play(data)
                websocket.send(messages['finished'])
            elif message == messages['exit']:
                continue_loop = False