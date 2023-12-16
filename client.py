import asyncio
import subprocess
from common.project import Project

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

# Start Websocket
client = WebSocketClient()
client.connect()

project = Project()
project.load_animation("animation")


def shutdown_raspberry_pi():
    """Call to shutdown the raspberry pi."""
    try:
        subprocess.run(["sudo", "shutdown", "-h", "now"])  # does not work
    except Exception as e:
        print(f"Cannot shutdown the raspberry pi: {e}")


def handler(msg):
    """Handle all messages from websocket."""
    if msg == WEBSOCKET_MESSAGES["play"]:
        project.play()
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif msg == WEBSOCKET_MESSAGES["auto"]:
        project.auto()

    elif msg == WEBSOCKET_MESSAGES["stop"]:
        project.stop()
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif msg == WEBSOCKET_MESSAGES["exit"]:
        project.rest()
        shutdown_raspberry_pi()


asyncio.run(client.ready(handler))
