import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# Configuration

kit.servo[0].set_pulse_width_range(600, 2400)
kit.servo[0].actuation_range = 180

# Run code

time.sleep(1)
kit.servo[0].angle = 90
time.sleep(1)

deg = 90

while deg != 0:
    deg = int(input('Starting at ', deg, ' deg. Do you want to move to another position?\n'))
    print('Moving to position ', deg, ' deg.')

    time.sleep(1)

    if deg < 0:
        deg = 0
    if deg > 180:
        deg = 180

    kit.servo[0].angle = deg
