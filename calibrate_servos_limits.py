from adafruit_servokit import ServoKit

from common.servo import initialize_servos, move_servo_to_angle
from common.validators import validate_controllable_servo
from mouth.config import servos_data

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

# Run code

while 1:
    print('\n\n\n', 'Next adjustment')
    servo = int(input('Select Servo: '))

    if validate_controllable_servo(servo) == False:
        continue

    position = int(input('Select start position in degrees: '))
    move_servo_to_angle(kit, servo, position, servos_data)

    
    print( 'Type "+" or "-" to adjust the position. Press any other key to exit.', '\n')

    while servo != None:
        operation = input('Adjusting: ')
        if operation == '+':
            position = position + 5
        elif operation == '-':
            position = position - 5
        else:
            servo = None

        if servo != None:
            move_servo_to_angle(kit, servo, position, servos_data)
