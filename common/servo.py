from common.config import servos_data, servos_connection, fabric_servo_data
from common.helpers import get_fabric_data
from common.validators import validate_servo, validate_servo_position


def validate_and_move(kit, servo: int, position: int):

    if validate_servo(servo) != True:
        return

    servo_position = validate_servo_position(servo, position)

    print('Validated servo #', servo, 'to position ', servo_position, ' deg.', '\n')

    kit.servo[servo].angle = servo_position


def move_servo_to_angle(kit, servo: int, position: int):

    validate_and_move(kit, servo, position)

    if servos_data[servo]['connection']:

        connection = servos_data[servo]['connection']

        if connection['type'] == 'normal':
            connection_position = position
        elif connection['type'] == 'inverted':
            connection_position = 180 - position

        validate_and_move(kit, connection['servo'], connection_position)


def initialize_servos(kit):

    i = 0
    available_servos = len(servos_data) - 1
    print('INITIALIZING SERVOS ', available_servos, '\n')

    while i <= available_servos:
        print('Configurating Servo #', i, '\n')

        fabric_data = get_fabric_data(i)
        min = fabric_data['pulse_width']['min']
        max = fabric_data['pulse_width']['max']
        actuation_range = fabric_data['actuation_range']

        print('type:', servos_data[i]['type'], ' min:', min,
              ' max:', max, ' actuation_range:', actuation_range, '\n\n')

        kit.servo[i].set_pulse_width_range(min, max)
        kit.servo[i].actuation_range = actuation_range
        i += 1

    print('END INITIALIZATION ', '\n\n\n')
