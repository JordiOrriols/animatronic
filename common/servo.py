from common.config import fabric_servo_data


class AniServo:
    def __init__(self, pin: int, type: str, min: int, max: int):
        self.pin = pin
        self.type = type
        self.physical_limits = {
            'min': min,
            'max': max
        }
        self.fabric_data = fabric_servo_data[type]

    def connect(self, servo: 'AniServo', direction: str):
        self.connection = servo
        self.connectionDirection = direction

    def start(self, kit):
        min = self.fabric_data['pulse_width']['min']
        max = self.fabric_data['pulse_width']['max']
        actuation_range = self.fabric_data['actuation_range']

        print('Servo #', self.pin,
              ' type:', self.type,
              ' min:', min,
              ' max:', max,
              ' actuation_range:', actuation_range,
              '\n')

        kit.servo[self.pin].set_pulse_width_range(min, max)
        kit.servo[self.pin].actuation_range = actuation_range
        self.kit = kit

        if(self.connection):
            self.connection.start()

    def __validate_position(self, position: int):

        if position < 0:
            print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
            position = 0

        minimum_phisical_limit = self.physical_limits['min']
        if position < minimum_phisical_limit:
            print('Minimum phisical limit exedeed ', position,
                  '. Moved to: ', minimum_phisical_limit, '\n')
            position = minimum_phisical_limit

        if position > self.fabric_data['actuation_range']:
            print('Position maximum exedeed ', position,
                  '. Moved to: ', self.fabric_data['actuation_range'], '\n')
            position = self.fabric_data['actuation_range']

        maximum_phisical_limit = self.physical_limits['max']
        if position > maximum_phisical_limit:
            print('Maximum phisical limit exedeed ', position,
                  '. Moved to: ', maximum_phisical_limit, '\n')
            position = maximum_phisical_limit

        return position

    def __move(self, position: int):
        servo_position = self.__validate_position(position)
        print('Moving servo #', self.pin,
              'to position ', servo_position, ' deg.')
        self.kit.servo[self.pin].angle = servo_position

    def move_to_angle(self, position: int):

        self.__move(position)

        if 'connection' in self:

            if self.connectionDirection == 'inverted':
                connection_position = 180 - position
            else:
                connection_position = position

            self.connection.move_to_angle(connection_position)


def initialize_servos(kit, servos_data: list['AniServo']):

    print('INITIALIZING SERVOS ', '\n\n')

    for servo in servos_data:
        servo.start(kit)

    print('END INITIALIZATION ', '\n\n')
