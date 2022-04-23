import time
import math

from common.servo import AniServo


class Animation:
    def __init__(self, data):
        self.__data = data
        self.__fps = int(self.__data['fps'])
        self.__frames = int(self.__data['frames'])
        self.__last_frame_position = self.__frames -1
        self.__positions = self.__data['positions']

        self.__frame_duration = 1 / self.__fps
        self.__total_duration = self.__frames / self.__fps

        print('Animation at ', self.__fps, 'fps')
        print('Total ',  self.__frames, ' Frames')
        print('Estimated duration: ',
              self.__total_duration, ' seconds')

    def start(self):
        self.__refresh_count = 0
        self.__elapsed_time = 0

        self.__start_time = time.time()
        self.__refresh_time = time.time()

    def refresh(self):
        self.__refresh_count = self.__refresh_count + 1
        self.__refresh_time = time.time()
        self.__elapsed_time = self.__refresh_time - self.__start_time

    def end(self):
        decimal_multiplier = 100
        print('Refresh count ', self.__refresh_count)
        print('Refresh rate ',  math.floor(
            self.__refresh_count / self.__elapsed_time), ' Hz')
        print('Interpolation factor ',  math.floor(
            self.__refresh_count / self.__frames * decimal_multiplier) / decimal_multiplier, ' times better')

    # Private Getters
    # Private Getters
    # Private Getters

    def __getCurrentFrame(self):
        current_frame =  math.floor(self.__elapsed_time / self.__frame_duration)

        if current_frame < self.__last_frame_position:
            return current_frame
        
        return self.__last_frame_position

    def __getNextFrame(self):
        current_frame = self.__getCurrentFrame()

        if current_frame < self.__last_frame_position:
            return current_frame + 1

        return self.__last_frame_position

    def __getFramePosition(self, servo: AniServo, frame: int):
        return int(self.__positions[servo.getName()][frame])

    def __getFrameTime(self, frame: int):
        return self.__frame_duration * frame

    # Interpolation
    # Interpolation
    # Interpolation

    def __interpolation(self, d, x):
        return d[0][1] + (x - d[0][0]) * ((d[1][1] - d[0][1])/(d[1][0] - d[0][0]))

    # Getters
    # Getters
    # Getters

    def getPositions(self):
        return self.__positions

    def getCurrentPosition(self, servo: AniServo):
        current_frame = self.__getCurrentFrame()
        next_frame = self.__getNextFrame()

        data = [
            [self.__getFrameTime(current_frame),
             self.__getFramePosition(servo, current_frame)],
            [self.__getFrameTime( next_frame),
             self.__getFramePosition(servo, next_frame)]
        ]

        try:
            return self.__interpolation(data, self.__elapsed_time)
        except:
            return self.__getFramePosition(servo, current_frame)

    # Checkers
    # Checkers
    # Checkers

    def inProgress(self):
        return self.__elapsed_time < self.__total_duration
