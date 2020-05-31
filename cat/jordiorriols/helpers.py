
import time
from cat.jordiorriols.config import fabric_servo_data, servos_data
from cat.jordiorriols.validators import validate_servo, validate_position

def get_fabric_data(servo):
    servo = validate_servo(servo)
    servo_type = servos_data[servo]['type']
    return fabric_servo_data[servo_type]


def move_servo_to_angle(kit, servo, position):
    print('Validating servo #', servo, ' and position ', position, ' deg.')

    servo = validate_servo(servo)
    position = validate_position(servo, position)
    time.sleep(1)

    print('Validated servo #', servo, 'to position ', position, ' deg.')

    time.sleep(2)

    print('Moving servo')

    time.sleep(5)

    kit.servo[servo].angle = position


def initialize_servos(kit):

    i = 0
    available_servos = len(servos_data) - 1

    while i < available_servos:
        print('Configurating Servo #', i, '\n')

        fabric_data = get_fabric_data(i)
        min = fabric_data['pulse_width']['min']
        max = fabric_data['pulse_width']['max']
        actuation_range = fabric_data['actuation_range']

        print('Servo data: type ', servos_data[i]['type'], ' min ', min, ' max ', max, '\n\n')

        kit.servo[i].set_pulse_width_range(min, max)
        kit.servo[i].actuation_range = actuation_range
        i += 1