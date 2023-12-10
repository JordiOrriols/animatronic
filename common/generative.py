import time
import random
from adafruit_servokit import ServoKit

from common.servo import AniServo
from common.logger import Logger


class GenerativeMovement(Logger):
    def __init__(self, servo: AniServo, max_duration=6, min_duration=1):
        super().__init__("GenerativeMovement - Servo #" + servo.getName())

        self.__servo = servo
        self.__max_duration = max_duration
        self.__min_duration = min_duration

        self.__in_progress = False
        self.__current_position = self.__servo.getCurrentPosition()
        self.__next_target_position = self.__servo.getCurrentPosition()
        self.__start_time = None
        self.__next_duration = None

    def __generate_smooth_movement(self):
        if self.__next_target_position and self.__next_duration:
            current_time = time.time() - self.__start_time
            progress = current_time / self.__next_duration

            if progress >= 1.0:
                progress = 1.0

            current_position = self.__current_position + progress * (
                self.__next_target_position - self.__current_position
            )
            self.__servo.move_to_angle(current_position)

            if progress == 1.0:
                self.__in_progress = False

    def __get_new_position(self, random_factor):
        min_limit = self.__servo.getPhysicalLimitMin()
        max_limit = self.__servo.getPhysicalLimitMax()

        actual_range = max_limit - min_limit
        limited_range = int((max_limit - min_limit) * (random_factor))
        offset = int((actual_range - limited_range) / 2)
        self.log(
            "Generating new position",
            {
                "actual_range": actual_range,
                "limited_range": limited_range,
                "random_factor": random_factor,
                "min_limit": min_limit,
                "max_limit": max_limit,
                "offset": offset,
            },
        )

        return random.randint(min_limit + offset, max_limit - offset)

    def __get_new_duration(self):
        return random.uniform(self.__min_duration, self.__max_duration)

    def update(self, random_factor=1.0):
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

        # Mover suavemente el servo a la posición almacenada
        self.__generate_smooth_movement()
