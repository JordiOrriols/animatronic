from mouth.mouth import adopt_phoneme
from common.initialize import initialize

# Initialization
servos_data, kit = initialize()

# Run code

while 1:
    print('\n\n\n', 'Next movement')
    phoneme = input('Select Phoneme: ')
    adopt_phoneme(phoneme, servos_data)
