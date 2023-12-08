from adafruit_servokit import ServoKit

from common.servo import initialize_servos
from mouth.mouth import adopt_phoneme
from mouth.config import servos_data

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

# Run code

while 1:
    print('\n\n\n', 'Next movement')
    phoneme = input('Select Phoneme: ')
    adopt_phoneme(kit, phoneme)
