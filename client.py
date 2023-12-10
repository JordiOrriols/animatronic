import subprocess
from common.project import Project

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

# Start Websocket
client = WebSocketClient()
client.connect()

project = Project()
project.load_animation('animation')


def shutdown_raspberry_pi():
    try:
        subprocess.run(['sudo', 'shutdown', '-h', 'now'])
    except Exception as e:
        print(f"Cannot shutdown the raspberry pi: {e}")

def handler(msg):

    if msg == WEBSOCKET_MESSAGES['play']:
        project.play()
        client.send(WEBSOCKET_MESSAGES['finished'])

    elif msg == WEBSOCKET_MESSAGES['exit']:
        shutdown_raspberry_pi()

client.ready(handler)