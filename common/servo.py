"""Servo module to handle servo information, limits and movements."""

from adafruit_servokit import ServoKit
import numpy as np

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

        self.__name = name
        self.__pin = pin
        self.__physical_limits_min = min_val
        self.__physical_limits_max = max_val
        self.__rest_position = rest_position
        self.__fabric_data = fabric_servo_data[servo_type]

        self.__connection: AniServo | None = None
        self.__connection_direction = None
        self.__servo = None

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

        self.sleep()

        if self.__connection is not None:
            self.__connection.start(kit)

    # Sleep
    def sleep(self):
        """Moving the servo to standby position."""
        self.move_to_angle(self.__rest_position)

    # Move
    def __validate_position(self, initial_position: int):
        position = np.clip(initial_position, 0, self.__physical_limits_max)
        position = np.clip(
            position, self.__physical_limits_min, self.__fabric_data["actuation_range"]
        )

        if self.debug_enabled():
            if initial_position is not position:
                self.log(
                    f"Invalid position detected {initial_position}. Moved to: {position}"
                )

        return position

    def __move(self, position: int):
        servo_position = self.__validate_position(position)
        self.__servo.angle = servo_position

    def move_to_angle(self, position: int):
        """Moving the servo to specific position."""
        self.__move(position)
        if self.__connection is not None:
            connection_position = np.where(
                self.__connection_direction == "inverted", 180 - position, position
            )
            self.__connection.move_to_angle(connection_position.item())


def initialize_servos(kit, servos_data):
    """Initialize all servos with ServoKit."""
    for servo in servos_data:
        servo.start(kit)

    print("Servos Initialized ", "\n")
