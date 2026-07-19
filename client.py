"""Client code."""

import asyncio
import subprocess
from common.project import Project

from common.websocket import WebSocketClient
from common.config import WEBSOCKET_MESSAGES

# Runtime objects are initialised lazily so the module can be imported safely in tests.
RUNTIME_STATE = {"client": None, "project": None}


def init_runtime():
    """Create the websocket client and project objects on first use."""
    if RUNTIME_STATE["client"] is None:
        RUNTIME_STATE["client"] = WebSocketClient()
        RUNTIME_STATE["client"].connect()

    if RUNTIME_STATE["project"] is None:
        RUNTIME_STATE["project"] = Project()
        RUNTIME_STATE["project"].load_animation("animation")

    return RUNTIME_STATE["client"], RUNTIME_STATE["project"]


def reboot_raspberry_pi():
    """Call to reboot the raspberry pi."""
    subprocess.run(["sudo", "reboot"], check=False)


def shutdown_raspberry_pi():
    """Call to shutdown the raspberry pi."""
    subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)


def handler(message):
    """Handle all messages from websocket."""
    runtime_client, runtime_project = init_runtime()

    if message["action"] == WEBSOCKET_MESSAGES["play"]:
        runtime_project.play()
        runtime_client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["auto-start"]:
        runtime_project.auto_start()

    elif message["action"] == WEBSOCKET_MESSAGES["auto-stop"]:
        runtime_project.auto_stop()
        runtime_client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["calibrate"]:
        runtime_project.calibrate(
            int(message["data"][0]["servo_pin"]), int(message["data"][0]["position"])
        )

    elif message["action"] == WEBSOCKET_MESSAGES["evaluate"]:
        runtime_project.evaluate()

    elif message["action"] == WEBSOCKET_MESSAGES["standby"]:
        runtime_project.standby()
        runtime_client.send(WEBSOCKET_MESSAGES["finished"])

    elif message["action"] == WEBSOCKET_MESSAGES["reboot"]:
        runtime_project.standby()
        reboot_raspberry_pi()

    elif message["action"] == WEBSOCKET_MESSAGES["exit"]:
        runtime_project.standby()
        shutdown_raspberry_pi()


def main():
    """Run the client event loop."""
    runtime_client, _ = init_runtime()
    asyncio.run(runtime_client.ready(handler))


if __name__ == "__main__":
    main()
