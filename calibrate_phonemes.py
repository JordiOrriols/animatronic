from adafruit_servokit import ServoKit
from tkinter import Tk, Frame, Scale, Label

from common.servo import initialize_servos, move_servo_to_angle
from mouth.config import servos_data
from common.validators import validate_controllable_servo

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit)

window = Tk()
window.title('Calibrate Phonemes')
window.geometry('850x300')

# Run code

def show_servo_scale(servo: int, min: int, max: int):

    frameControl = Frame(window)
    frameControl.pack(side='left', padx=15)
    
    label = '#' + str(servo)
    n = Label(frameControl, fg='black', width=3, text=label)
    n.pack(side='top', expand=True)

    def print_selection(v):
        l.config(text=v)
        move_servo_to_angle(kit, servo, int(v))

    s = Scale(frameControl, from_=min, to=max, length=200,
                 showvalue=0, tickinterval=2, resolution=5, command=print_selection)

    s.pack(side='top', expand=True)

    l = Label(frameControl, bg='white', fg='black', width=3, text='...')
    l.pack(side='top', expand=True)

for i in range(len(servos_data)):

    if validate_controllable_servo(i) == False:
        continue

    min = servos_data[i]['physical_limits']['min']
    max = servos_data[i]['physical_limits']['max']
    show_servo_scale(i, min, max)

window.mainloop()
