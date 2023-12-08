import json

from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from skeletonV2.config import servos_data
from common.animation import Animation

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

# Run code

with open('skeletonV2/animation.json') as json_file:
    data = json.load(json_file)
    animation = Animation(data)

    while 1:

        start = input('Press any key to start: ')
        animation.start()

        while animation.inProgress():

            animation.refresh()

            for servo in servos_data:
                if servo.getName() in animation.getPositions().keys():
                    new_position = animation.getCurrentPosition(servo)
                    servo.move_to_angle(int(new_position))

        animation.end()
