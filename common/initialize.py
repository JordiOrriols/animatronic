import os

from dotenv import load_dotenv
from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from skeleton.config import skeleton_servos_data
from skeletonV2.config import skeletonV2_servos_data
from common.animation import Animation

servos_data_object = {
    'skeleton': skeleton_servos_data,
    'skeletonV2': skeletonV2_servos_data,
}

def initialize():
    load_dotenv()

    print('Initializing for project: ', os.getenv('PROJECT_ID'), '\n')

    servos_data = get_servos_data()

    kit = ServoKit(channels=16)
    initialize_servos(kit, servos_data)

    return servos_data, kit

def get_servos_data():
    servos_data = servos_data_object[os.getenv('PROJECT_ID')]

    if servos_data == None:
        print('Servo Data not initialized. Wrong Project ID', os.getenv('PROJECT_ID'), '\n')
        return None
    
    return servos_data

def play(json_file):

    servos_data = get_servos_data()

    if servos_data == None:
        return

    animation = Animation(json_file)

    animation.start()

    while animation.inProgress():

        animation.refresh()

        for servo in servos_data:
            if servo.getName() in animation.getPositions().keys():
                new_position = animation.getCurrentPosition(servo)
                servo.move_to_angle(int(new_position))

    animation.end()

    for servo in servos_data:
        servo.sleep()

