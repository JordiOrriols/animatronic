import time
import numpy as np

from common.servo import AniServo
from common.logger import Logger


class Animation(Logger):
    """Animation class will handle everything related to the JSON animation."""

    def __init__(self, data):
        super().__init__("Animation")

        self.__data = data
        self.__fps = int(self.__data["fps"])
        self.__frames = int(self.__data["frames"])
        self.__last_frame_position = self.__frames - 1
        self.__positions = self.__data["positions"]

        self.__refresh_count = 0
        self.__elapsed_time = 0
        self.__start_time = 0
        self.__refresh_time = 0

        self.__frame_duration = 1 / self.__fps
        self.__total_duration = self.__frames / self.__fps

        self.info(f"Animation at {self.__fps} fps")
        self.info(f"Total {self.__frames} Frames")
        self.info(f"Estimated duration: {self.__total_duration} seconds")

    def start(self):
        """Call before animation starts to initialize animation data."""
        self.__refresh_count = 0
        self.__elapsed_time = 0
        self.__start_time = time.time()
        self.__refresh_time = self.__start_time

    def refresh(self):
        """Call on each iteration for the animation."""
        self.__refresh_count += 1
        self.__refresh_time = time.time()
        self.__elapsed_time = self.__refresh_time - self.__start_time

    def end(self):
        """Call when animation has ended to print performance metrics."""
        decimal_multiplier = 100
        interpolation_factor = (
            np.floor(self.__refresh_count / self.__frames * decimal_multiplier)
            / decimal_multiplier
        )
        self.info(f"Refresh count {self.__refresh_count}")
        self.info(
            f"Refresh rate {np.floor(self.__refresh_count / self.__elapsed_time)} Hz"
        )

        self.info(f"Interpolation factor {interpolation_factor} times better")

    def __get_current_frame(self):
        return np.minimum(
            self.__last_frame_position,
            np.floor(self.__elapsed_time / self.__frame_duration),
        )

    def __get_next_frame(self, current_frame):
        # return np.minimum(current_frame + 1, self.__last_frame_position) Chat GPT optimization
        if current_frame < self.__last_frame_position:
            return current_frame + 1

        return self.__last_frame_position

    def __get_frame_position(self, servo: AniServo, frame: int):
        return np.int_(self.__positions[servo.get_name()][frame])

    def __get_frame_time(self, frame: int):
        return self.__frame_duration * frame

    def __interpolation(self, d, x):
        x_values, y_values = np.array(d).T
        return np.interp(x, x_values, y_values)

    def get_positions(self):
        """Get all positions from the whole animation."""
        return self.__positions

    def get_current_position(self, servo: AniServo):
        """Get the current position for a specific servo on the animation."""
        current_frame = self.__get_current_frame()
        next_frame = self.__get_next_frame(current_frame)

        data = [
            [
                self.__get_frame_time(current_frame),
                self.__get_frame_position(servo, current_frame),
            ],
            [
                self.__get_frame_time(next_frame),
                self.__get_frame_position(servo, next_frame),
            ],
        ]

        try:
            return self.__interpolation(data, self.__elapsed_time)
        except Exception as e:
            self.error(f"Interpolation failed: {e}")
            return self.__get_frame_position(servo, current_frame)

    def in_progress(self):
        """Know if the animation still in progress. Will return false when the animation does not have any other keyframe to play."""
        return self.__elapsed_time < self.__total_duration
