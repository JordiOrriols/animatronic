"""Server code."""

import json
import asyncio
from time import sleep
from playsound import playsound
from simple_term_menu import TerminalMenu

from websockets.server import serve

from common.autodiscovery import AutoDiscoveryServer
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES

# Auto Discovery - UDP BROADCAST
auto_discovery = AutoDiscoveryServer()
auto_discovery.start()

async def show_options(websocket):
    """Show cli options to choose what to do with your animatronic."""

    options = [
        "[p] Play animation",
        "[a] Automatic mode",
        "[c] Calibrate",
        "[s] Standby",
        "[r] Reboot",
        "[e] Exit",
    ]
    terminal_menu = TerminalMenu(options, title="Select next action")
    menu_entry_index = terminal_menu.show()

    print(f"You have selected {options[menu_entry_index]}!")

    if menu_entry_index == 0:
        print("Playing Animation:")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["play"])
        sleep(1)
        playsound("sound/background.mp3", False)
        playsound("sound/laugh.mp3", False)

    elif menu_entry_index == 1:
        print("Automatic mode:")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["auto_start"])
        playsound("sound/background.mp3", False)
        input("Press any key to stop")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["auto_stop"])

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
                await sendMessage(
                    websocket,
                    WEBSOCKET_MESSAGES["calibrate"],
                    {"servo_pin": servo_pin, "position": position},
                )

        await sendMessage(websocket, WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 3:
        print("Standby:")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 4:
        print("Reboot:")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["reboot"])

    elif menu_entry_index == 5:
        print("Exit:")
        await sendMessage(websocket, WEBSOCKET_MESSAGES["exit"])

    else:
        print("Option not supported:")


async def handler(websocket):
    """Handle websocket client messages."""
    async for msg in websocket:
        message = json.loads(msg)
        print(f"Message received: {message}")

        if message["action"] == WEBSOCKET_MESSAGES["connected"]:
            auto_discovery.disable()

        if message["action"] in (
            [WEBSOCKET_MESSAGES["ready"], WEBSOCKET_MESSAGES["finished"]]
        ):
            await sendMessage(websocket, WEBSOCKET_MESSAGES["waiting"])
            await show_options(websocket)


async def sendMessage(websocket, action: str, *data):
    """Send message to the client."""
    msg = json.dumps({"action": action, "data": data})
    await websocket.send(msg)
    print("Message sent", msg)


async def main():
    """Main function to keep your server running."""
    current_ip = auto_discovery.get_current_ip()

    print("Websocket Server Started")
    print(f" - Websocket url ws://{str(current_ip)}:{str(WEBSOCKET_PORT)}")

    async with serve(handler, current_ip, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
