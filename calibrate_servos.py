from adafruit_servokit import ServoKit

from common.servo import initialize_servos, move_servo_to_angle

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit)

# Run code

while 1:
    print('\n\n\n', 'Next adjustment')
    servo = input('Select Servo: ')
    position = input('Select start position in degrees: ')
    move_servo_to_angle(kit, int(servo), int(position))

    
    print( 'Type "+" or "-" to adjust the position. Press any other key to exit.', '\n')

    while servo:
        operation = input('Adjusting: ')
        if operation == '+':
            position = int(position) + 5
        elif operation == '-':
            position = int(position) - 5
        else:
            servo = None

        if servo:
            move_servo_to_angle(kit, int(servo), int(position))
