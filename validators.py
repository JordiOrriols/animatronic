import helpers
import config

# Validators


def validate_servo(servo):

    if servo < 0:
        print('Servo index minimum exedeed ', servo, '. Moved to: 0', '\n')
        servo = 0

    available_servos = len(servos_data) - 1

    if servo > available_servos:
        print('Servo index maximum exedeed ', servo,
              '. Moved to: ', available_servos, '\n')
        servo = available_servos

    return servo


def validate_position(position):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
        position = 0

    if position > 180:
        print('Position maximum exedeed ', position, '. Moved to: 180', '\n')
        position = 180

    return position


def validate_servo_position(servo, position):

    if position < 0:
        print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
        position = 0

    minimum_phisical_limit = config.servos_data[servo]['phisical_limit']['min']
    if position < minimum_phisical_limit:
        print('Minimum phisical limit exedeed ', position,
              '. Moved to: ', minimum_phisical_limit, '\n')
        position = minimum_phisical_limit

    fabric_data = helpers.get_fabric_data(servo)

    if position > config.fabric_data['actuation_range']:
        print('Position maximum exedeed ', position,
              '. Moved to: ', config.fabric_data['actuation_range'], '\n')
        position = config.fabric_data['actuation_range']

    maximum_phisical_limit = config.servos_data[servo]['phisical_limit']['max']
    if position < maximum_phisical_limit:
        print('Maximum phisical limit exedeed ', position,
              '. Moved to: ', maximum_phisical_limit, '\n')
        position = maximum_phisical_limit

    return position