"""Server code."""

import json
import asyncio
from time import sleep
from playsound import playsound
from simple_term_menu import TerminalMenu
from websockets.server import serve

from common.autodiscovery import AutoDiscoveryServer
from common.logger import Logger
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES


logger = Logger("Server")


def _print_banner():
    print("")
    logger.info("┌──────────────────────────────────────┐")
    logger.info("│ Animatronics Controller V0.0.5       │")
    logger.info("│ by Jordi Orriols                     │")
    logger.info("└──────────────────────────────────────┘")
    print("")
    logger.info("Starting discovery, checking websockets")
    print("")

# Auto Discovery - UDP BROADCAST
auto_discovery = None


def get_auto_discovery():
    """Initialise the auto-discovery service lazily for import-safe testing."""
    global auto_discovery
    if auto_discovery is None:
        auto_discovery = AutoDiscoveryServer()
        auto_discovery.start()
    return auto_discovery


async def show_options(websocket):
    """Show cli options to choose what to do with your animatronic."""

    options = [
        "[p] Play animation",
        "[a] Automatic mode",
        "[c] Calibrate",
        "[e] Evaluate",
        "[s] Standby",
        "[r] Reboot",
        "[e] Exit",
    ]
    terminal_menu = TerminalMenu(options, title="Select next action")
    menu_entry_index = terminal_menu.show()

    print("")
    logger.info(f"You have selected {options[menu_entry_index]}!")
    print("")

    if menu_entry_index == 0:
        logger.success("Playing Animation:")
        await send_message(websocket, WEBSOCKET_MESSAGES["play"])
        sleep(1)
        playsound("sound/background.mp3", False)
        playsound("sound/laugh.mp3", False)

    elif menu_entry_index == 1:
        logger.success("Automatic mode:")
        await send_message(websocket, WEBSOCKET_MESSAGES["auto-start"])
        playsound("sound/background.mp3", False)
        input("Press any key to stop")
        await send_message(websocket, WEBSOCKET_MESSAGES["auto-stop"])

    elif menu_entry_index == 2:
        logger.info("Calibrate:")
        await calibrate(websocket)

    elif menu_entry_index == 3:
        logger.info("Evaluate:")
        await send_message(websocket, WEBSOCKET_MESSAGES["evaluate"])

    elif menu_entry_index == 4:
        logger.warning("Standby:")
        await send_message(websocket, WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 5:
        logger.warning("Reboot:")
        await send_message(websocket, WEBSOCKET_MESSAGES["reboot"])

    elif menu_entry_index == 6:
        logger.error("Exit:")
        await send_message(websocket, WEBSOCKET_MESSAGES["exit"])

    else:
        logger.error("Option not supported:")


async def handler(websocket):
    """Handle websocket client messages."""
    async for msg in websocket:
        message = json.loads(msg)
        logger.info(f"Message received: {message}")

        if message["action"] == WEBSOCKET_MESSAGES["connected"]:
            discovery = auto_discovery if auto_discovery is not None else get_auto_discovery()
            if discovery is not None:
                discovery.disable()

        if message["action"] in (
            [WEBSOCKET_MESSAGES["ready"], WEBSOCKET_MESSAGES["finished"]]
        ):
            await send_message(websocket, WEBSOCKET_MESSAGES["waiting"])
            await show_options(websocket)


async def calibrate(websocket):
    """Calibrate servo."""
    servo_pin = int(input("Write Servo Pin: "))
    position = int(input("Select start position in degrees: "))

    logger.input('Type "+" or "-" to adjust the position. Press any other key to exit.')
    print("")

    while position is not None:
        operation = input("Adjusting: ")
        if operation == "+":
            position = position + 5
        elif operation == "-":
            position = position - 5
        else:
            position = None

        if position is not None:
            await send_message(
                websocket,
                WEBSOCKET_MESSAGES["calibrate"],
                {"servo_pin": servo_pin, "position": position},
            )

    await send_message(websocket, WEBSOCKET_MESSAGES["standby"])


async def send_message(websocket, action: str, *data):
    """Send message to the client."""
    msg = json.dumps({"action": action, "data": data})
    await websocket.send(msg)
    logger.success("Message sent", msg)


async def main():
    """Main function to keep your server running."""
    _print_banner()
    current_ip = get_auto_discovery().get_current_ip()

    logger.success("Websocket Server Started")
    logger.info(f"Websocket url ws://{str(current_ip)}:{str(WEBSOCKET_PORT)}")
    print("")

    async with serve(handler, current_ip, WEBSOCKET_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
