import time
from adafruit_servokit import ServoKit

# Declaration

servos_data = [
    {'type': 'big', 'physical_limits': {'min': 0, 'max': 180}}, #0
    {'type': 'big', 'physical_limits': {'min': 0, 'max': 180}}, #1

    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #2
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #3
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #4
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #5
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #6
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #7
    {'type': 'blue', 'physical_limits': {'min': 0, 'max': 180}}, #8
]


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


def validate_position(servo, position):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0')
        position = 0

    minimum_phisical_limit = servos_data[servo]['phisical_limit']['min']
    if position < minimum_phisical_limit:
        print('Minimum phisical limit exedeed ', position, '. Moved to: ', minimum_phisical_limit)
        position = minimum_phisical_limit

    if position > 180:
        print('Position maximum exedeed ', position, '. Moved to: 180')
        position = 180

    maximum_phisical_limit = servos_data[servo]['phisical_limit']['max']
    if position < maximum_phisical_limit:
        print('Maximum phisical limit exedeed ', position, '. Moved to: ', maximum_phisical_limit)
        position = maximum_phisical_limit

    return position


# Helpers

def move_servo_to_angle(servo, position):
    print('Validating servo #', servo, ' and position ', position, ' deg.')

    time.sleep(1)

    servo = validate_servo(servo)
    position = validate_position(servo, position)

    print('Moving servo #', servo, 'to position ', position, ' deg.')

    time.sleep(3)

    kit.servo[servo].angle = position
    kit.servo[0].angle = position


# Run code

while 1:
    servo = input('Select Servo:\n')
    position = input('Select position in degrees?\n')
    move_servo_to_angle(int(servo), int(position))

    time.sleep(1)
