import time
import random

from common.servo import AniServo
from common.logger import Logger


class GenerativeMovement(Logger):
    """GenerativeMovement Class will generate random movements in the servos limits."""

    def __init__(self, servo: AniServo, max_duration=6, min_duration=1):
        super().__init__("GenerativeMovement - Servo #" + servo.get_name())

        self.__servo = servo
        self.__max_duration = max_duration
        self.__min_duration = min_duration

        self.__in_progress = False
        self.__current_position = self.__servo.get_current_position()
        self.__next_target_position = self.__servo.get_current_position()
        self.__start_time = None
        self.__next_duration = None

        # Precompute servo limits
        self.__min_limit = self.__servo.get_physical_limit_min()
        self.__max_limit = self.__servo.get_physical_limit_max()

        # Calculate range parameters
        self.__actual_range = self.__max_limit - self.__min_limit

    def __generate_smooth_movement(self):
        if self.__next_target_position and self.__next_duration:
            current_time = time.time() - self.__start_time
            progress = min(current_time / self.__next_duration, 1.0)

            current_position = self.__current_position + progress * (
                self.__next_target_position - self.__current_position
            )
            self.__servo.move_to_angle(current_position)

            if progress == 1.0:
                self.__in_progress = False

    def __get_new_position(self, random_factor):
        limited_range = int(self.__actual_range * random_factor)
        offset = int((self.__actual_range - limited_range) / 2)

        return random.randint(self.__min_limit + offset, self.__max_limit - offset)

    def __get_new_duration(self):
        return random.uniform(self.__min_duration, self.__max_duration)

    def update(self, random_factor=1.0):
        """This method will calculate new positions if needed, and move all the servos to the next position."""
        if not self.__in_progress:
            self.__in_progress = True
            self.__start_time = time.time()
            self.__current_position = self.__next_target_position
            self.__next_target_position = self.__get_new_position(random_factor)
            self.__next_duration = self.__get_new_duration()

            self.log(
                "Generating new position",
                {
                    "current_position": self.__current_position,
                    "new_position": self.__next_target_position,
                    "duration": self.__next_duration,
                },
            )

        self.__generate_smooth_movement()
