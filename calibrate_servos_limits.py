from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from mouth.config import servos_data

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

# Run code

while 1:
    print('\n\n\n', 'Next adjustment')

    servo = None
    selected_servo = int(input('Select Servo: '))

    for current_servo in servos_data:
        if(current_servo.getPin() == selected_servo):
            servo = current_servo

    if servo == None:
        continue

    position = int(input('Select start position in degrees: '))
    servo.move_to_angle(position)

    print('Type "+" or "-" to adjust the position. Press any other key to exit.', '\n')

    while servo != None:
        operation = input('Adjusting: ')
        if operation == '+':
            position = position + 5
        elif operation == '-':
            position = position - 5
        else:
            servo = None

        if servo != None:
            servo.move_to_angle(position)
