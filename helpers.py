
import time

import config
import validators

def get_fabric_data(servo):
    servo = validators.validate_servo(servo)
    servo_type = config.servos_data[servo]['type']
    return config.fabric_servo_data[servo_type]


def move_servo_to_angle(kit, servo, position):
    print('Validating servo #', servo, ' and position ', position, ' deg.', '\n')

    servo = validators.validate_servo(servo)
    position = validators.validate_servo_position(servo, position)

    print('Validated servo #', servo, 'to position ', position, ' deg.', '\n')

    time.sleep(5)
    kit.servo[servo].angle = position


def initialize_servos(kit):

    i = 0
    available_servos = len(config.servos_data) - 1
    print('INITIALIZING SERVOS ', available_servos, '\n')

    while i < available_servos:
        print('Configurating Servo #', i, '\n')

        fabric_data = get_fabric_data(i)
        min = fabric_data['pulse_width']['min']
        max = fabric_data['pulse_width']['max']
        actuation_range = fabric_data['actuation_range']

        print('type:', config.servos_data[i]['type'], ' min:', min, ' max:', max, ' actuation_range:', actuation_range, '\n\n')

        kit.servo[i].set_pulse_width_range(min, max)
        kit.servo[i].actuation_range = actuation_range
        i += 1
        
    print('END INITIALIZATION ', '\n\n\n')