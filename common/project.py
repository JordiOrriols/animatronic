import os
import json

from dotenv import load_dotenv
from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from projects.skeleton.config import skeleton_servos_data
from projects.skeletonV2.config import skeletonV2_servos_data
from projects.jackSparrow.config import jackSparrow_servos_data
from common.animation import Animation
from common.logger import Logger

servos_data_object = {
    'skeleton': skeleton_servos_data,
    'skeletonV2': skeletonV2_servos_data,
    'jackSparrow': jackSparrow_servos_data
}

class Project(Logger):
    def __init__(self, init_servos = True):
        super(self, 'Project')

        self.info('Loading environment...')
        load_dotenv()

        self.__project = os.getenv('PROJECT_ID')
        self.__animation_data = None

        self.info('Initializing for project: ', self.__project)
        self.__servos_data = servos_data_object[self.__project]

        if self.__validate_servos_data():
            kit = ServoKit(channels=16)
            self.kit = kit
            if init_servos:
                initialize_servos(kit, self.__servos_data)

    def __validate_servos_data(self):
       if self.__servos_data == None:
            self.info('Servo Data not initialized. Wrong Project ID', self.__project)
            return False
       return True

    def get_servos_data(self):
        if self.__validate_servos_data():
            return self.__servos_data

    def load_animation(self, animation_name):
        with open('projects/' + self.__project + '/' + animation_name + '.json') as json_file:

            self.__animation_data = json.load(json_file)

    def play(self):

        if self.__validate_servos_data():

            animation = Animation(self.__animation_data) # maybe we can move to load animation

            animation.start()

            while animation.inProgress():

                animation.refresh()

                for servo in self.__servos_data:
                    if servo.getName() in animation.getPositions().keys():
                        new_position = animation.getCurrentPosition(servo)
                        servo.move_to_angle(int(new_position))

            animation.end()

