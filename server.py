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


async def show_options(websocket, capabilities=None, servos=None):
    """Show cli options to choose what to do with your animatronic.

    Options are filtered by the connected client's reported `capabilities` (sent on
    the client-ready message), so a project without e.g. an animation.json won't
    offer "Play animation"/"Evaluate". Missing capability keys default to True so
    older clients that don't report capabilities still see the full menu.
    """
    capabilities = capabilities or {}
    servos = servos or []
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
        await calibrate(websocket, servos)

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
    servos = []
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
                    capabilities = data[0].get("capabilities", {})
                    servos = data[0].get("servos", [])

            if message["action"] in (
                [WEBSOCKET_MESSAGES["ready"], WEBSOCKET_MESSAGES["finished"]]
            ):
                await send_message(websocket, WEBSOCKET_MESSAGES["waiting"])
                await show_options(websocket, capabilities, servos)
    except ConnectionClosed:
        logger.warning("Client disconnected")


async def _adjust_value(websocket, servo_pin: int, label: str, start_value: int) -> int:
    """Interactively nudge a value in +/-5 degree increments, sending a live
    calibrate-move preview after every nudge. Any other input confirms and
    returns the current value."""
    value = start_value
    logger.input(f'{label}: type "+" or "-" to adjust. Press any other key to confirm.')
    while True:
        operation = input(f"{label} ({value}): ")
        if operation == "+":
            value += 5
        elif operation == "-":
            value -= 5
        else:
            return value
        await send_message(
            websocket,
            WEBSOCKET_MESSAGES["calibrate-move"],
            {"servo_pin": servo_pin, "position": value},
        )


async def _calibrate_servo(websocket, servo: dict):
    """Run the Neutral -> Min -> Max guided calibration flow for one servo, then
    send calibrate-save with the confirmed values."""
    name = servo["name"]
    pin = servo["pin"]
    print("")
    logger.info(f"Calibrating '{name}' (pin {pin})")

    neutral_input = input("Neutral position in degrees [90]: ")
    neutral = int(neutral_input) if neutral_input.strip() else 90
    await send_message(
        websocket, WEBSOCKET_MESSAGES["calibrate-move"], {"servo_pin": pin, "position": neutral}
    )
    neutral = await _adjust_value(websocket, pin, "Neutral", neutral)
    minimum = await _adjust_value(websocket, pin, "Min", servo.get("min", 0))
    maximum = await _adjust_value(websocket, pin, "Max", servo.get("max", 180))

    await send_message(
        websocket,
        WEBSOCKET_MESSAGES["calibrate-save"],
        {"servo_pin": pin, "neutral": neutral, "min": minimum, "max": maximum},
    )


async def calibrate(websocket, servos=None):
    """Calibrate one servo or all servos: Neutral -> Min -> Max per servo, then
    persist+push everything once at the end of the session."""
    servos = servos or []
    if not servos:
        logger.error("No servos reported by client; cannot calibrate.")
        return

    options = ["[all] Calibrate ALL servos"] + [
        f"{servo['name']} (pin {servo['pin']}) - min {servo['min']} max {servo['max']}"
        f" rest {servo['rest']}"
        for servo in servos
    ]
    terminal_menu = TerminalMenu(options, title="Select servo to calibrate")
    menu_entry_index = terminal_menu.show()
    if not isinstance(menu_entry_index, int):
        logger.error("No servo selected:")
        return

    targets = servos if menu_entry_index == 0 else [servos[menu_entry_index - 1]]

    for servo in targets:
        await _calibrate_servo(websocket, servo)

    await send_message(websocket, WEBSOCKET_MESSAGES["calibrate-commit"])
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
