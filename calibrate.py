import time
from adafruit_servokit import ServoKit


# Configuration

kit = ServoKit(channels=16)

i = 0
while i < 15:
    kit.servo[i].set_pulse_width_range(600, 2400)
    kit.servo[i].actuation_range = 180
    i += 1


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


# Helpers

def move_servo_to_angle(servo, position):
    print('Moving servo #', servo, 'to position ', position, ' deg.')

    time.sleep(2)
    servo = validate_servo(int(servo))
    position = validate_position(int(position))

    kit.servo[servo].angle = position


# Run code

while 1:
    servo = input('Select Servo:\n')
    position = input('Select position in degrees?\n')
    move_servo_to_angle(servo, position)
