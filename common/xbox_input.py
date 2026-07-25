"""XboxInputReader module, used by the SERVER to read a physical Xbox controller.

The server has the physical Xbox controller attached. `XboxInputReader` wraps
`pygame.joystick` to poll raw stick/trigger values and produces a small flat dict of
named, normalized values (deadzone applied to sticks, triggers normalized to
0.0..1.0) that gets sent as-is over the websocket to the client, which maps them to
servo angles via `XboxServoMapper` (see common/xbox_servo_mapper.py).
"""

# pylint: disable=import-outside-toplevel
# pygame is imported lazily inside each method below so this module (and anything that
# imports it, like server.py) can be imported without pygame installed when no physical
# Xbox controller is being used.
from common.logger import Logger

# Named axis indices for a standard Xbox controller as reported by pygame/SDL2 on macOS.
# NOTE: exact indices can vary slightly between controller models (wired/Bluetooth) and
# pygame/SDL versions. If mappings look wrong for your hardware, enable debug logging
# (`XboxInputReader(...).debug()`) to print raw axis values and adjust this table.
AXIS_INDEX = {
    "left_stick_x": 0,
    "left_stick_y": 1,
    "right_stick_x": 2,
    "right_stick_y": 3,
    "left_trigger": 4,
    "right_trigger": 5,
}

# Axes that report -1.0 (released) .. 1.0 (fully pressed) and should be normalized to
# 0.0..1.0 instead of being treated like a centered stick axis.
TRIGGER_AXES = ("left_trigger", "right_trigger")

DEFAULT_DEADZONE = 0.08


class XboxInputReader(Logger):
    """Reads an Xbox controller connected to this machine using `pygame.joystick`."""

    def __init__(self, deadzone: float = DEFAULT_DEADZONE):
        super().__init__("XboxInputReader")
        self.__deadzone = deadzone
        self.__joystick = None

    def connect(self) -> bool:
        """Initialize pygame and try to grab the first connected controller."""
        import pygame  # imported lazily so importing this module never requires pygame

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.error("No Xbox controller detected")
            return False

        self.__joystick = pygame.joystick.Joystick(0)
        self.__joystick.init()
        self.info("Controller connected: ", self.__joystick.get_name())
        return True

    def is_connected(self) -> bool:
        """Check whether a controller is still connected."""
        import pygame

        return self.__joystick is not None and pygame.joystick.get_count() > 0

    def disconnect(self):
        """Release the controller and shut down the joystick subsystem."""
        import pygame

        if self.__joystick is not None:
            self.__joystick.quit()
            self.__joystick = None
        pygame.joystick.quit()

    def __apply_deadzone(self, value: float) -> float:
        return 0.0 if abs(value) < self.__deadzone else value

    def poll_axes(self) -> dict:
        """Read the current state of all mapped axes/triggers.

        Returns a flat dict, e.g. {"left_stick_x": 0.0, ..., "right_trigger": 0.0}, with
        stick values in -1.0..1.0 (deadzone applied) and trigger values in 0.0..1.0.
        """
        import pygame

        pygame.event.pump()

        values = {}
        for name, index in AXIS_INDEX.items():
            try:
                raw = self.__joystick.get_axis(index)
            except (pygame.error, IndexError):
                continue

            if name in TRIGGER_AXES:
                values[name] = max(0.0, min(1.0, (raw + 1.0) / 2.0))
            else:
                values[name] = self.__apply_deadzone(raw)

        self.log("Raw axes: ", values)
        return values
