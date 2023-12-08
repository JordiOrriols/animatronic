import os

from dotenv import load_dotenv
from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from skeleton.config import skeleton_servos_data
from skeletonV2.config import skeletonV2_servos_data
from common.animation import Animation
from common.servo import AniServo

servos_data = None
servos_data_object = {
    'skeleton': skeleton_servos_data,
    'skeletonV2': skeletonV2_servos_data,
}

def initialize():
    load_dotenv()

    servos_data: list[AniServo] = servos_data_object[os.getenv('PROJECT_ID')]

    kit = ServoKit(channels=16)
    initialize_servos(kit, servos_data)

    return servos_data, kit

def play(animation_name):

    if servos_data == None:
        print('Servo Data not initialized. Execute start function.', '\n')
        return

    with open(os.getenv('PROJECT_ID') + '/' + animation_name + '.json') as json_file:

        animation = Animation(json_file)

        animation.start()

        while animation.inProgress():

            animation.refresh()

            for servo in servos_data:
                if servo.getName() in animation.getPositions().keys():
                    new_position = animation.getCurrentPosition(servo)
                    servo.move_to_angle(int(new_position))

        animation.end()
