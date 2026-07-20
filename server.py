"""Server code."""

import json
import asyncio
import threading
from time import sleep
from playsound import playsound
from simple_term_menu import TerminalMenu
from websockets.server import serve

from common.autodiscovery import AutoDiscoveryServer
from common.logger import Logger
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES
from common.xbox_controller import XboxInputReader


logger = Logger("Main")


def _print_banner():
    print("")
    print("")
    print("┌──────────────────────────────────────┐")
    print("│ Animatronics Controller V0.0.5       │")
    print("│ by Jordi Orriols                     │")
    print("└──────────────────────────────────────┘")
    print("")
    print("")
    logger.info("Starting discovery, checking websockets")
    print("")

# Auto Discovery - UDP BROADCAST
RUNTIME_STATE = {"auto_discovery": None}
auto_discovery = None


def get_auto_discovery():
    """Initialise the auto-discovery service lazily for import-safe testing."""
    if RUNTIME_STATE["auto_discovery"] is None:
        RUNTIME_STATE["auto_discovery"] = AutoDiscoveryServer()
        RUNTIME_STATE["auto_discovery"].start()

    globals()["auto_discovery"] = RUNTIME_STATE["auto_discovery"]
    return RUNTIME_STATE["auto_discovery"]


async def show_options(websocket):
    """Show cli options to choose what to do with your animatronic."""

    options = [
        "[p] Play animation",
        "[a] Automatic mode",
        "[x] Xbox controller",
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
        logger.success("Xbox Controller:")
        await xbox_control(websocket)

    elif menu_entry_index == 3:
        logger.info("Calibrate:")
        await calibrate(websocket)

    elif menu_entry_index == 4:
        logger.info("Evaluate:")
        await send_message(websocket, WEBSOCKET_MESSAGES["evaluate"])

    elif menu_entry_index == 5:
        logger.warning("Standby:")
        await send_message(websocket, WEBSOCKET_MESSAGES["standby"])

    elif menu_entry_index == 6:
        logger.warning("Reboot:")
        await send_message(websocket, WEBSOCKET_MESSAGES["reboot"])

    elif menu_entry_index == 7:
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
            discovery = (
                RUNTIME_STATE["auto_discovery"]
                if RUNTIME_STATE["auto_discovery"] is not None
                else get_auto_discovery()
            )
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


async def xbox_control(websocket, poll_interval: float = 0.05):
    """Read the Xbox controller and stream servo positions to the client in near
    real-time until the user presses a key or the controller is disconnected."""
    reader = XboxInputReader()
    if not reader.connect():
        return

    await send_message(websocket, WEBSOCKET_MESSAGES["xbox-start"])

    stop_event = threading.Event()

    def wait_for_stop():
        input("Press any key to stop")
        stop_event.set()

    threading.Thread(target=wait_for_stop, daemon=True).start()

    disconnected = await xbox_stream_loop(websocket, reader, stop_event, poll_interval)

    await send_message(websocket, WEBSOCKET_MESSAGES["xbox-stop"])
    if disconnected:
        await send_message(websocket, WEBSOCKET_MESSAGES["standby"])
    reader.disconnect()


async def xbox_stream_loop(websocket, reader, stop_event, poll_interval: float = 0.05) -> bool:
    """Poll the controller and send positions until stopped. Returns True if the
    controller was disconnected (as opposed to a user-initiated stop)."""
    while not stop_event.is_set():
        if not reader.is_connected():
            logger.warning("Xbox controller disconnected")
            return True

        axes = reader.poll_axes()
        await send_message(websocket, WEBSOCKET_MESSAGES["xbox-position"], axes)
        await asyncio.sleep(poll_interval)

    return False


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
