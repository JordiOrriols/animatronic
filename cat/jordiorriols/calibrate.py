import time
from adafruit_servokit import ServoKit

from cat.jordiorriols.helpers import move_servo_to_angle, initialize_servos


# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit)

# Run code

while 1:
    print('\n\n\n', 'Next movement')
    servo = input('Select Servo: ')
    position = input('Select position in degrees? ')
    move_servo_to_angle(kit, int(servo), int(position))

    time.sleep(1)
