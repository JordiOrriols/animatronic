from mouth.mouth import adopt_phoneme
from common.project import Project

# Initialization
project = Project()       

# Run code

while 1:
    print('\n\n\n', 'Next movement')
    phoneme = input('Select Phoneme: ')
    adopt_phoneme(phoneme, project.get_servos_data())
