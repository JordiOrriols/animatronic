from common.helpers import get_fabric_data
from common.config import servos_data

# Validators

def validate_controllable_servo(servo: int):

    valid_servo = validate_servo(servo)

    if valid_servo == False:
        return False

    for i in range(len(servos_data)):
        if 'connection' in servos_data[i] and servos_data[i]['connection']['servo'] == servo:
            print('Servo ', servo, ' is controlled by ', i, '\n')
            return False

    return True

def validate_servo(servo: int):

    if servo < 0:
        print('Servo index minimum exedeed ', servo, '\n')
        return False

    available_servos = len(servos_data) - 1

    if servo > available_servos:
        print('Servo index maximum exedeed ', servo, '\n')
        return False

    if servos_data[servo]['type'] == 'disabled':
        print('Servo disabled ', servo, '\n')
        return False

    return True


def validate_position(position: int):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
        position = 0

    if position > 180:
        print('Position maximum exedeed ', position, '. Moved to: 180', '\n')
        position = 180

    return position


def validate_servo_position(servo: int, position: int):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
        position = 0

    minimum_phisical_limit = servos_data[servo]['physical_limits']['min']
    if position < minimum_phisical_limit:
        print('Minimum phisical limit exedeed ', position,
              '. Moved to: ', minimum_phisical_limit, '\n')
        position = minimum_phisical_limit

    fabric_data = get_fabric_data(servo)

    if position > fabric_data['actuation_range']:
        print('Position maximum exedeed ', position,
              '. Moved to: ', fabric_data['actuation_range'], '\n')
        position = fabric_data['actuation_range']

    maximum_phisical_limit = servos_data[servo]['physical_limits']['max']
    if position > maximum_phisical_limit:
        print('Maximum phisical limit exedeed ', position,
              '. Moved to: ', maximum_phisical_limit, '\n')
        position = maximum_phisical_limit

    return position
