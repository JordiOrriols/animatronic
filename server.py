"""Server code."""

import json
import asyncio
import threading
from time import sleep
from playsound import playsound
from simple_term_menu import TerminalMenu
from websockets import serve
from websockets.exceptions import ConnectionClosed

from common.autodiscovery import AutoDiscoveryServer
from common.logger import Logger
from common.websocket import WEBSOCKET_PORT, WEBSOCKET_MESSAGES
from common.xbox_input import XboxInputReader


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


async def show_options(websocket, capabilities=None):
    """Show cli options to choose what to do with your animatronic.

    Options are filtered by the connected client's reported `capabilities` (sent on
    the client-ready message), so a project without e.g. an animation.json won't
    offer "Play animation"/"Evaluate". Missing capability keys default to True so
    older clients that don't report capabilities still see the full menu.
    """
    capabilities = capabilities or {}
    has_animation = capabilities.get("animation", True)
    has_generative = capabilities.get("generative", True)
    has_xbox = capabilities.get("xbox", True)

    menu_items = []
    if has_animation:
        menu_items.append(("play", "[p] Play animation"))
    if has_generative:
        menu_items.append(("auto", "[a] Automatic mode"))
    if has_xbox:
        menu_items.append(("xbox", "[x] Xbox controller"))
    menu_items.append(("calibrate", "[c] Calibrate"))
    if has_animation:
        menu_items.append(("evaluate", "[e] Evaluate"))
    menu_items.append(("standby", "[s] Standby"))
    menu_items.append(("reboot", "[r] Reboot"))
    menu_items.append(("exit", "[e] Exit"))

    options = [label for _, label in menu_items]
    terminal_menu = TerminalMenu(options, title="Select next action")
    menu_entry_index = terminal_menu.show()
    if not isinstance(menu_entry_index, int):
        logger.error("No option selected:")
        return
    selected_key, selected_label = menu_items[menu_entry_index]

    print("")
    logger.info(f"You have selected {selected_label}!")
    print("")

    if selected_key == "play":
        logger.success("Playing Animation:")
        await send_message(websocket, WEBSOCKET_MESSAGES["play"])
        sleep(1)
        playsound("sound/background.mp3", False)
        playsound("sound/laugh.mp3", False)

    elif selected_key == "auto":
        logger.success("Automatic mode:")
        await send_message(websocket, WEBSOCKET_MESSAGES["auto-start"])
        playsound("sound/background.mp3", False)
        input("Press any key to stop")
        await send_message(websocket, WEBSOCKET_MESSAGES["auto-stop"])

    elif selected_key == "xbox":
        logger.success("Xbox Controller:")
        await xbox_control(websocket)

    elif selected_key == "calibrate":
        logger.info("Calibrate:")
        await calibrate(websocket)

    elif selected_key == "evaluate":
        logger.info("Evaluate:")
        await send_message(websocket, WEBSOCKET_MESSAGES["evaluate"])

    elif selected_key == "standby":
        logger.warning("Standby:")
        await send_message(websocket, WEBSOCKET_MESSAGES["standby"])

    elif selected_key == "reboot":
        logger.warning("Reboot:")
        await send_message(websocket, WEBSOCKET_MESSAGES["reboot"])

    elif selected_key == "exit":
        logger.error("Exit:")
        await send_message(websocket, WEBSOCKET_MESSAGES["exit"])

    else:
        logger.error("Option not supported:")


async def handler(websocket):
    """Handle websocket client messages."""
    capabilities = {}
    try:
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

            if message["action"] == WEBSOCKET_MESSAGES["ready"]:
                data = message.get("data") or []
                if data and isinstance(data[0], dict):
                    capabilities = data[0]

            if message["action"] in (
                [WEBSOCKET_MESSAGES["ready"], WEBSOCKET_MESSAGES["finished"]]
            ):
                await send_message(websocket, WEBSOCKET_MESSAGES["waiting"])
                await show_options(websocket, capabilities)
    except ConnectionClosed:
        logger.warning("Client disconnected")


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
