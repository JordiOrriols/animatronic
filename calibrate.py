import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# Configuration

kit.servo[0].set_pulse_width_range(600, 2400)
kit.servo[0].actuation_range = 180

# Run code

while 1:
    servo = input('Select Servo:\n')
    position = input('Select position in degrees?\n')
    move_servo_to_angle(servo, position)

# Helpers

def move_servo_to_angle(servo, position):
    print('Moving servo #', servo, 'to position ', position, ' deg.')

    time.sleep(2)
    servo = validate_servo(int(servo))
    position = validate_position(int(position))

    kit.servo[servo].angle = position


# Validators

def validate_servo(servo):

    if servo < 0:
        print('Servo minimum exedeed ', servo, '. Moved to: 0')
        servo = 0

    if servo > 15:
        print('Servo maximum exedeed ', servo, '. Moved to: 15')
        servo = 15

    return servo

def validate_position(position):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0')
        position = 0

    if position > 180:
        print('Position maximum exedeed ', position, '. Moved to: 180')
        position = 180

    return position
    