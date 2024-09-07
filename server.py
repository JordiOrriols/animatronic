"""Server code."""

import asyncio
import json
from time import sleep
from playsound import playsound
from simple_term_menu import TerminalMenu

from websockets.server import serve

from common.autodiscovery import AutoDiscoveryServer
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES

# Auto Discovery - UDP BROADCAST
auto_discovery = AutoDiscoveryServer()
auto_discovery.start()

# Websocket


async def show_options(websocket):
    """Show cli options to choose what to do with your animatronic."""

    options = [
        "[p] Play animation",
        "[a] Automatic mode",
        "[c] Calibrate",
        "[s] Standby",
        "[e] Exit",
    ]
    terminal_menu = TerminalMenu(options, title="Select next action")
    menu_entry_index = terminal_menu.show()

    print(f"You have selected {options[menu_entry_index]}!")

    if menu_entry_index == 0:
        print("Playing Animation:")
        await websocket.send(WEBSOCKET_MESSAGES["play"])
        sleep(1)
        playsound("sound/background.mp3", False)
        playsound("sound/laugh.mp3", False)

    elif menu_entry_index == 1:
        print("Automatic mode:")
        await websocket.send(WEBSOCKET_MESSAGES["auto_start"])
        playsound("sound/background.mp3", False)
        input("Press any key to stop")
        await websocket.send(WEBSOCKET_MESSAGES["auto_stop"])

    elif menu_entry_index == 2:
        print("Calibrate:")

        servo_pin = int(input("Write Servo Pin: "))
        position = int(input("Select start position in degrees: "))

        print(
            'Type "+" or "-" to adjust the position. Press any other key to exit.', "\n"
        )

        while position is not None:
            operation = input("Adjusting: ")
            if operation == "+":
                position = position + 5
            elif operation == "-":
                position = position - 5
            else:
                position = None

            if position is not None:
                print("Angle", position)
                await websocket.send(
                    WEBSOCKET_MESSAGES["calibrate"], {servo_pin, position}
                )

        await websocket.send(WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 3:
        print("Standby:")
        await websocket.send(WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 4:
        print("Exit:")
        await websocket.send(WEBSOCKET_MESSAGES["exit"])

    else:
        print("Option not supported:")


async def handler(websocket):
    """Handle websocket client messages."""
    async for message in websocket:

        print("Websocket Message: ", message)
        msg = json.loads(message)

        if msg.action == WEBSOCKET_MESSAGES["connected"]:
            auto_discovery.disable()

        if msg.action in (
            [WEBSOCKET_MESSAGES["ready"], WEBSOCKET_MESSAGES["finished"]]
        ):
            await websocket.send(WEBSOCKET_MESSAGES["waiting"])
            await show_options(websocket)


async def main():
    """Main function to keep your server running."""
    current_ip = auto_discovery.get_current_ip()

    print("Websocket Server Started")
    print(f" - Websocket url ws://{str(current_ip)}:{str(WEBSOCKET_PORT)}")

    async with serve(handler, current_ip, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
