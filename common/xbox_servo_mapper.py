"""XboxServoMapper module, used by the CLIENT to map Xbox axis values to servo angles.

The client owns the physical servos. `XboxServoMapper` takes a project's
`xbox_settings` config (per-servo axis mapping, similar in spirit to
`generative_settings`) and maps the raw values received from the server (produced by
`XboxInputReader`, see common/xbox_input.py) into target servo angles, applying a
small amount of smoothing so movement isn't jittery while still feeling near
real-time.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from common.logger import Logger
from common.xbox_input import TRIGGER_AXES

if TYPE_CHECKING:
    # Only needed for type hints. Importing it unconditionally would drag in
    # adafruit_servokit (and its hardware detection), which this module's users on the
    # SERVER side don't need/have.
    from common.servo import AniServo


class XboxServoMapper(Logger):
    """Maps raw Xbox controller axis values to servo target angles.

    Config dictionary supported keys per servo, keyed by servo name (all but `input`
    are optional):
      - input: axis name (see `common.xbox_input.AXIS_INDEX`) that drives this servo
        (required)
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
