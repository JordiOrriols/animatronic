import os
import json
from common.initialize import initialize, play

# Initialization
initialize()

# Run code

animation_name = 'animation'

with open(os.getenv('PROJECT_ID') + '/' + animation_name + '.json') as json_file:
    data = json.load(json_file)
    
    while 1:
        input('Press any key to start: ')
        play(data)
