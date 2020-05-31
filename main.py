from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

kit.servo[0].set_pulse_width_range(600, 2400)
kit.servo[0].actuation_range = 180
kit.servo[0].angle = 90