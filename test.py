import time
from websockets.sync.client import connect
from common.socket import url, port, messages

with connect("ws://" + url + ":" + str(port)) as websocket:

    websocket.send(messages['connected'])

    websocket.send(messages['ready'])
    continue_loop = True

    while continue_loop:

        message = websocket.recv()
        print(f"Socket Event: {message}")

        if message == messages['play']:

            time.sleep(5)
            websocket.send(messages['finished'])
        elif message == messages['exit']:
            continue_loop = False