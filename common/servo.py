"""Servo module to handle servo information, limits and movements."""

from typing import Optional
import math
import time

from adafruit_servokit import ServoKit

from common.config import fabric_servo_data
from common.logger import Logger


class AniServo(Logger):
    """Aniservo class to handle servo information, limits and movements."""

    def __init__(
        self,
        name: str,
        pin: int,
        servo_type: str,
        min_val: int,
        max_val: int,
        rest_position: int,
    ):
        super().__init__("AniServo " + str(name) + " on pin #" + str(pin))

        self.__fabric_data = fabric_servo_data[servo_type]

        self.__name = name
        self.__pin = pin

        self.__connection: Optional[AniServo] = None
        self.__connection_direction: Optional[str] = None
        self.__servo = None

        self.set_calibration(min_val, max_val, rest_position)

    # Getters
    def get_name(self):
        """Getting the servo name."""
        return self.__name

    def get_pin(self):
        """Getting the servo pin."""
        return self.__pin

    def get_physical_limit_min(self):
        """Getting the servo min physical limit."""
        return self.__physical_limits_min

    def get_physical_limit_max(self):
        """Getting the servo max physical limit."""
        return self.__physical_limits_max

    def get_rest_position(self):
        """Getting the servo position when robot is on standby."""
        return self.__rest_position

    def get_current_position(self):
        """Getting the servo current position."""
        if self.__servo is None:
            return self.__rest_position
        return self.__servo.angle

    # Connect
    def connect(self, servo: "AniServo", direction: str):
        """Connecting to an another servo that should be controlled at the same time."""
        self.__connection = servo
        self.__connection_direction = direction

    # Start
    def start(self, kit: ServoKit):
        """Starting the servo class with all the information, and adafruit ServoKit."""
        self.__servo = kit.servo[self.__pin]
        self.__servo.set_pulse_width_range(
            self.__fabric_data["pulse_width"]["min"],
            self.__fabric_data["pulse_width"]["max"],
        )
        self.__servo.actuation_range = self.__fabric_data["actuation_range"]

        if self.__connection is not None:
            self.__connection.start(kit)

        self.sleep()

    # Sleep
    def sleep(self):
        """Return to neutral using the reusable eased movement."""
        self.move_to_angle_eased(self.__rest_position)

    @staticmethod
    def apply_easing(progress: float, ease_in: float = 0.2, ease_out: float = 0.2) -> float:
        """Apply the shared generative ease-in/ease-out formula to progress."""
        for name, value in (("progress", progress), ("ease_in", ease_in), ("ease_out", ease_out)):
            if (
                isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name} must be a finite number")
        if not 0 <= ease_in <= 1 or not 0 <= ease_out <= 1:
            raise ValueError("ease_in and ease_out must be between 0 and 1")
        eased = max(0.0, min(1.0, progress))
        if ease_in > 0:
            eased = eased ** (1.0 + ease_in * 3.0)
        if ease_out > 0:
            eased = 1.0 - (1.0 - eased) ** (1.0 + ease_out * 3.0)
        return eased

    def move_to_angle_eased(
        self, position: float, duration_ms: float = 1000,
        ease_in: float = 0.2, ease_out: float = 0.2,
    ) -> None:
        """Move to a calibrated target with easing; block until the duration finishes."""
        self.apply_easing(0, ease_in, ease_out)
        if (
            isinstance(duration_ms, bool) or not isinstance(duration_ms, (int, float))
            or not math.isfinite(duration_ms) or duration_ms < 0
        ):
            raise ValueError("duration_ms must be a finite non-negative number")
        if not math.isfinite(position):
            raise ValueError(f"Invalid servo angle for {self.__name}: {position}")
        if self.__servo is None:
            return
        target = self.__validate_position(position)
        start = self.get_current_position()
        if start is None:
            self.warning("Current angle is unknown; cannot ease the initial movement command.")
            self.move_to_angle(target)
            return
        duration = duration_ms / 1000
        if duration == 0 or start == target:
            self.move_to_angle(target)
            return
        started = time.monotonic()
        while True:
            progress = min((time.monotonic() - started) / duration, 1.0)
            position = start + (target - start) * self.apply_easing(progress, ease_in, ease_out)
            # Calibration can leave the current angle outside the new limits.
            self.move_to_calibration_angle(position)
            if self.__connection is not None:
                linked = (
                    180 - position if self.__connection_direction == "inverted" else position
                )
                self.__connection.move_to_calibration_angle(linked)
            if progress >= 1:
                return
            time.sleep(0.02)

    # Move
    def __validate_position(self, initial_position: int):
        position = min(initial_position, self.__physical_limits_max)
        position = max(position, self.__physical_limits_min)
        return position

    def __write_angle(self, position: float):
        if not math.isfinite(position):
            raise ValueError(f"Invalid servo angle for {self.__name}: {position}")
        if self.__servo is None:
            return
        self.__servo.angle = position

    def __move(self, position: float):
        servo_position = self.__validate_position(position)
        if self.__servo is None:
            return
        self.__write_angle(servo_position)

    def move_to_angle(self, position: float):
        """Moving the servo to specific position."""
        self.__move(position)
        if self.__connection is not None:
            if self.__connection_direction == "inverted":
                connection_position = 180 - position
            else:
                connection_position = position

            if self.__connection.get_current_position() is not None:
                self.__connection.move_to_angle(connection_position)

    def move_to_calibration_angle(self, position: float):
        """Moving the servo while searching for new calibration bounds. Bypasses
        the currently configured min/max limits, clamping only to the physical
        actuation range of the servo's fabric data."""
        servo_position = min(position, self.__fabric_data["actuation_range"])
        servo_position = max(servo_position, 0)
        if self.__servo is None:
            return
        self.__write_angle(servo_position)

    def set_calibration(self, min_val: int, max_val: int, rest_position: int):
        """Updating the servo's calibrated limits and rest position at runtime."""
        self.__physical_limits_min = max(min_val, 0)
        self.__physical_limits_max = min(max_val, self.__fabric_data["actuation_range"])
        self.__rest_position = rest_position

    def to_calibration_dict(self):
        """Getting this servo's current calibration as a plain dict."""
        return {
            "min": self.__physical_limits_min,
            "max": self.__physical_limits_max,
            "rest": self.__rest_position,
        }


def initialize_servos(kit, servos_data):
    """Initialize all servos with ServoKit."""
    initialized = False
    try:
        for servo in servos_data:
            servo.start(kit)
        initialized = True
    finally:
        if not initialized:
            for servo in servos_data:
                servo.sleep()

    print("Servos Initialized ", "\n")
