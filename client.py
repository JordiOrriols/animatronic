"""Client code."""

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


def reboot_raspberry_pi():
    """Call to reboot the raspberry pi."""
    subprocess.run(["sudo", "reboot"], check=False)


def shutdown_raspberry_pi():
    """Call to shutdown the raspberry pi."""
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)


def handler(message):
    """Handle all messages from websocket."""

    if message["action"] == WEBSOCKET_MESSAGES["play"]:
        project.play()
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["auto-start"]:
        project.auto_start()

    elif message["action"] == WEBSOCKET_MESSAGES["auto-stop"]:
        project.auto_stop()
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["calibrate"]:
        project.calibrate(
            int(message["data"][0]["servo_pin"]), int(message["data"][0]["position"])
        )

    elif message["action"] == WEBSOCKET_MESSAGES["evaluate"]:
        project.evaluate()

    elif message["action"] == WEBSOCKET_MESSAGES["standby"]:
        project.standby()
        client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["reboot"]:
        project.standby()
        reboot_raspberry_pi()

    elif message["action"] == WEBSOCKET_MESSAGES["exit"]:
        project.standby()
        shutdown_raspberry_pi()


asyncio.run(client.ready(handler))
