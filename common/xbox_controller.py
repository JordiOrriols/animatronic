"""XboxController module to control servos in near real-time via an Xbox controller.

Two responsibilities live in this single module on purpose, since both revolve around
the same physical device and the feature is small enough to stay self-contained:

`XboxInputReader` (used by the SERVER, which has the physical Xbox controller attached):
  - Wraps `pygame.joystick` to poll raw stick/trigger values.
  - Produces a small flat dict of named, normalized values (deadzone applied to sticks,
    triggers normalized to 0.0..1.0) that gets sent as-is over the websocket.

`XboxServoMapper` (used by the CLIENT, which owns the physical servos):
  - Takes a project's `xbox_settings` config (per-servo axis mapping, similar in spirit
    to `generative_settings`) and maps the raw values received from the server into
    target servo angles, applying a small amount of smoothing so movement isn't jittery
    while still feeling near real-time.
"""

from typing import Optional

from common.servo import AniServo
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


class XboxServoMapper(Logger):
    """Maps raw Xbox controller axis values to servo target angles.

    Config dictionary supported keys per servo, keyed by servo name (all but `input`
    are optional):
      - input: axis name (see `AXIS_INDEX`) that drives this servo (required)
      - invert: bool, flips the axis direction
      - min_angle, max_angle: bounds (deg) to use for targets (clipped to servo limits)
      - smoothing: 0.0..1.0 fraction of the remaining distance covered per update
        (higher = snappier/less eased, lower = smoother/more lag)
    """

    DEFAULTS = {
        "invert": False,
        "min_angle": None,
        "max_angle": None,
        "smoothing": 0.35,
    }

    def __init__(self, servos_data: list[AniServo], xbox_settings: Optional[dict] = None):
        super().__init__("XboxServoMapper")

        self.__servos = {servo.get_name(): servo for servo in servos_data}
        self.__settings = {}

        settings = {} if xbox_settings is None else xbox_settings
        for servo_name, cfg in settings.items():
            if servo_name not in self.__servos:
                continue
            merged = dict(cfg)
            for key, value in self.DEFAULTS.items():
                merged.setdefault(key, value)
            self.__settings[servo_name] = merged

        self.__current_positions: dict[str, float] = {}
        self.reset()

    def reset(self):
        """Seed internal smoothing state from each mapped servo's current position."""
        for servo_name in self.__settings:
            servo = self.__servos[servo_name]
            self.__current_positions[servo_name] = float(servo.get_current_position())

    def __get_angle_bounds(self, servo: AniServo, cfg: dict):
        lower_bound = servo.get_physical_limit_min()
        upper_bound = servo.get_physical_limit_max()

        if cfg["min_angle"] is not None:
            lower_bound = max(lower_bound, int(cfg["min_angle"]))
        if cfg["max_angle"] is not None:
            upper_bound = min(upper_bound, int(cfg["max_angle"]))

        if lower_bound > upper_bound:
            lower_bound, upper_bound = upper_bound, lower_bound

        return lower_bound, upper_bound

    def __map_to_angle(self, servo: AniServo, cfg: dict, raw_value: float) -> float:
        lower_bound, upper_bound = self.__get_angle_bounds(servo, cfg)

        # Triggers already arrive normalized 0.0..1.0; sticks arrive -1.0..1.0 and need
        # to be re-centered into a 0.0..1.0 progress value along the angle range.
        is_trigger = cfg["input"] in TRIGGER_AXES
        progress = raw_value if is_trigger else (raw_value + 1.0) / 2.0
        progress = max(0.0, min(1.0, progress))

        if cfg["invert"]:
            progress = 1.0 - progress

        return lower_bound + (upper_bound - lower_bound) * progress

    def update(self, raw_axes: dict):
        """Advance every mapped servo towards its new target based on `raw_axes`.

        Non-blocking; safe to call every time a new position message is received.
        """
        for servo_name, cfg in self.__settings.items():
            input_name = cfg["input"]
            if input_name not in raw_axes:
                continue

            servo = self.__servos[servo_name]
            target = self.__map_to_angle(servo, cfg, raw_axes[input_name])

            current = self.__current_positions.get(
                servo_name, float(servo.get_current_position())
            )
            smoothing = float(cfg["smoothing"])
            current = current + (target - current) * smoothing

            self.__current_positions[servo_name] = current
            servo.move_to_angle(int(round(current)))
