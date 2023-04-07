import json
import time
from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from skeleton.config import servos_data

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
        print('\n', 'Estimated duration: ', data['frames'] / data['fps'], ' seconds')
        start = input('Press any key to start: ')

        current_frame = 0
        positions = data['positions']
        start = time.time()
        frameDuration = 1 / data['fps']

        while current_frame < data['frames']:

            frameStart = time.time()

            for servo in servos_data:
                if servo.getName() in positions.keys():
                    new_position = positions[servo.getName()][current_frame]
                    servo.move_to_angle(int(new_position))
            
            frameEnd = time.time()
            frameElapsed = frameEnd - frameStart
            sleepTime = frameDuration - frameElapsed

            if sleepTime > 0:
                time.sleep(sleepTime)
            
            current_frame = current_frame + 1
        
        end = time.time()

        print('\n', 'Estimated duration: ', data['frames'] / data['fps'], ' seconds')
        print('\n', 'Final duration: ', end - start, ' seconds')