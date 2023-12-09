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
        self.__debug = False

        self.__info('Animation at ', self.__fps, 'fps')
        self.__info('Total ',  self.__frames, ' Frames')
        self.__info('Estimated duration: ',
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
        self.__info('Refresh count ', self.__refresh_count)
        self.__info('Refresh rate ',  math.floor(
            self.__refresh_count / self.__elapsed_time), ' Hz')
        self.__info('Interpolation factor ',  math.floor(
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
            self.__error('Interpolation failed')
            return self.__getFramePosition(servo, current_frame)

    # Log
    # Log
    # Log

    def debug(self):
        self.__debug = True

    def __log(self, level: str, *message):
        if self.__debug:
            print(level, 'Animation - ',
                  message,
                  '\n')

    def __info(self, *message):
        self.__log('Info: ', message)

    def __error(self, *message):
        self.__log('ERROR: ', message)

    # Checkers
    # Checkers
    # Checkers

    def inProgress(self):
        return self.__elapsed_time < self.__total_duration
