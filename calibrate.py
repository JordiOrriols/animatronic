import time
from adafruit_servokit import ServoKit

import helpers


# Initialization
kit = ServoKit(channels=16)

helpers.initialize_servos(kit)

# Run code

while 1:
    print('\n\n\n', 'Next movement')
    servo = input('Select Servo: ')
    position = input('Select position in degrees? ')
    helpers.move_servo_to_angle(kit, int(servo), int(position))

    time.sleep(1)
