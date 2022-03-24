from common.config import fabric_servo_data


class AniServo:
    def __init__(self, name: str, pin: int, type: str, min: int, max: int, rest_position: int):
        self.__name = name
        self.__pin = pin
        self.__type = type
        self.__physical_limits_min = min
        self.__physical_limits_max = max
        self.__rest_position = rest_position
        self.__fabric_data = fabric_servo_data[type]

    # Getters
    # Getters
    # Getters

    def getName(self):
        return self.__name
    
    def getPin(self):
        return self.__pin

    def getPhysicalLimitMin(self):
        return self.__physical_limits_min
    
    def getPhysicalLimitMax(self):
        return self.__physical_limits_max

    # Connect
    # Connect
    # Connect

    def connect(self, servo: 'AniServo', direction: str):
        self.__connection = servo
        self.__connectionDirection = direction

    # Start
    # Start
    # Start

    def start(self, kit):
        min = self.__fabric_data['pulse_width']['min']
        max = self.__fabric_data['pulse_width']['max']
        actuation_range = self.__fabric_data['actuation_range']

        print('Servo #', self.__pin,
              ' type:', self.__type,
              ' min:', min,
              ' max:', max,
              ' actuation_range:', actuation_range,
              '\n')

        kit.servo[self.pin].set_pulse_width_range(min, max)
        kit.servo[self.pin].actuation_range = actuation_range
        self.__kit = kit

        self.sleep()

        if(self.__connection):
            self.__connection.start()
    
    # Sleep
    # Sleep
    # Sleep

    def sleep(self):
        self.move_to_angle(self.__rest_position)

    # Move
    # Move
    # Move

    def __validate_position(self, position: int):

        if position < 0:
            print('Position minimum exedeed ', position, '. Moved to: 0', '\n')
            position = 0

        minimum_phisical_limit = self.__physical_limits_min
        if position < minimum_phisical_limit:
            print('Minimum phisical limit exedeed ', position,
                  '. Moved to: ', minimum_phisical_limit, '\n')
            position = minimum_phisical_limit

        if position > self.__fabric_data['actuation_range']:
            print('Position maximum exedeed ', position,
                  '. Moved to: ', self.fabric_data['actuation_range'], '\n')
            position = self.__fabric_data['actuation_range']

        maximum_phisical_limit = self.__physical_limits_max
        if position > maximum_phisical_limit:
            print('Maximum phisical limit exedeed ', position,
                  '. Moved to: ', maximum_phisical_limit, '\n')
            position = maximum_phisical_limit

        return position

    def __move(self, position: int):
        servo_position = self.__validate_position(position)
        print('Moving servo #', self.__pin,
              'to position ', servo_position, ' deg.')
        self.__kit.servo[self.__pin].angle = servo_position

    def move_to_angle(self, position: int):

        self.__move(position)

        if 'connection' in self:

            if self.__connectionDirection == 'inverted':
                connection_position = 180 - position
            else:
                connection_position = position

            self.__connection.move_to_angle(connection_position)


def initialize_servos(kit, servos_data: list['AniServo']):

    print('INITIALIZING SERVOS ', '\n\n')

    for servo in servos_data:
        servo.start(kit)

    print('END INITIALIZATION ', '\n\n')
