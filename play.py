import json
import time
from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from mouth.mouth import adopt_phoneme
from scheleton.config import servos_data

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

# Run code

with open('scheleton/animation.json') as json_file:
    data = json.load(json_file)

    print('Animation loaded')

    while 1:
        print('\n\n', 'System Ready')
        print('\n', 'Playing at ', data['fps'], 'fps')
        print('\n', data['frames'], 'Frames')
        start = input('Press any key to start: ')

        current_frame = 0
        fps = data['fps']
        frames = data['frames']
        positions = data['positions']

        while current_frame < frames:
            for servo in servos_data:
                if servo.getName() in positions.keys():
                    new_position = positions[servo.getName()][current_frame]
                    servo.move_to_angle(int(new_position))
            
            time.sleep(1 / fps)

