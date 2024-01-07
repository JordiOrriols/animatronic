"""Calibrating servos module via command line interface."""

from common.project import Project
from common.servo import AniServo

# Initialization
project = Project(True)

# Run code

while 1:
    print("\n\n\n", "Next adjustment")

    SERVO = None
    selected_servo = input("Write Servo Pin: ")
    SERVOS_DATA = project.get_servos_data()

    if SERVOS_DATA is not None:
        for current_servo in SERVOS_DATA:
            if current_servo.get_pin() == int(selected_servo):
                SERVO = current_servo

    if SERVO is None:
        continue

    print(SERVO.get_name(), "\n")
    SERVO.start(project.kit)

    position = int(input("Select start position in degrees: "))
    SERVO.move_to_angle(position)

    print('Type "+" or "-" to adjust the position. Press any other key to exit.', "\n")

    while SERVO is not None:
        operation = input("Adjusting: ")
        if operation == "+":
            position = position + 5
        elif operation == "-":
            position = position - 5
        else:
            SERVO = None

        if SERVO is not None:
            print("Angle", position)
            SERVO.move_to_angle(position)
