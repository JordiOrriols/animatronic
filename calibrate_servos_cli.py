from common.initialize import initialize

# Initialization
servos_data, kit = initialize()

# Run code

while 1:
    print('\n\n\n', 'Next adjustment')

    servo = None
    selected_servo = input('Write Servo Pin: ')

    for current_servo in servos_data:
        if(current_servo.getPin() == int(selected_servo)):
            servo = current_servo

    if servo == None:
        continue

    print(servo.getName(), '\n')
    servo.start(kit)

    position = int(input('Select start position in degrees: '))
    servo.move_to_angle(position)

    print('Type "+" or "-" to adjust the position. Press any other key to exit.', '\n')

    while servo != None:
        operation = input('Adjusting: ')
        if operation == '+':
            position = position + 5
        elif operation == '-':
            position = position - 5
        else:
            servo = None

        if servo != None:
            print('Angle', position)
            servo.move_to_angle(position)
