from common.config import servos_data, fabric_servo_data
from common.helpers import get_fabric_data
from common.validators import validate_servo, validate_servo_position


def validate_and_move(kit, servo: int, position: int):

    if validate_servo(servo) == False:
        return

    servo_position = validate_servo_position(servo, position)
    print('Moving servo #', servo, 'to position ', servo_position, ' deg.', '\n')
    kit.servo[servo].angle = servo_position


def move_servo_to_angle(kit, servo: int, position: int):

    validate_and_move(kit, servo, position)

    if servos_data[servo]['connection']:

        connection = servos_data[servo]['connection']

        if connection['type'] == 'inverted':
            connection_position = 180 - position
        else :
            connection_position = position

        validate_and_move(kit, connection['servo'], connection_position)

def initialize_servos(kit):

    print('INITIALIZING SERVOS ', '\n\n')

    for i in range(len(servos_data)):

        if servos_data[i]['type'] == 'disabled':
            continue

        fabric_data = get_fabric_data(i)
        min = fabric_data['pulse_width']['min']
        max = fabric_data['pulse_width']['max']
        actuation_range = fabric_data['actuation_range']

        print('Servo #', i, 'type:', servos_data[i]['type'], ' min:', min,
              ' max:', max, ' actuation_range:', actuation_range, '\n')

        kit.servo[i].set_pulse_width_range(min, max)
        kit.servo[i].actuation_range = actuation_range

    print('END INITIALIZATION ', '\n\n')
