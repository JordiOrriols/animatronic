from common.project import Project
from common.servo import AniServo

# Initialization
project = Project(False)

# Run code

while 1:
    print("\n\n\n", "Next adjustment")

    servo: AniServo | None = None
    selected_servo = input("Write Servo Pin: ")

    for current_servo in project.get_servos_data():
        if current_servo.get_pin() == int(selected_servo):
            servo = current_servo

    if servo is None:
        continue

    print(servo.get_name(), "\n")
    servo.start(project.kit)

    position = int(input("Select start position in degrees: "))
    servo.move_to_angle(position)

    print('Type "+" or "-" to adjust the position. Press any other key to exit.', "\n")

    while servo is not None:
        operation = input("Adjusting: ")
        if operation == "+":
            position = position + 5
        elif operation == "-":
            position = position - 5
        else:
            servo = None

        if servo is not None:
            print("Angle", position)
            servo.move_to_angle(position)
