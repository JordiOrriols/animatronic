from adafruit_servokit import ServoKit
from tkinter import Tk, Frame, Scale, Label

from common.servo import AniServo, initialize_servos
from scheleton.config import servos_data

# Initialization
kit = ServoKit(channels=16)

initialize_servos(kit, servos_data)

window = Tk()
window.title('Calibrate Phonemes')
window.geometry('850x300')

# Run code


def show_servo_scale(servo: AniServo):

    frameControl = Frame(window)
    frameControl.pack(side='left', padx=15)

    label = '#' + str(servo.getPin())
    n = Label(frameControl, fg='black', width=3, text=label)
    n.pack(side='top', expand=True)

    def print_selection(v):
        l.config(text=v)
        servo.move_to_angle(int(v))

    s = Scale(frameControl, from_=servo.getPhysicalLimitMin(), to=servo.getPhysicalLimitMax(), length=200,
              showvalue=servo.getRestPosition(), tickinterval=2, resolution=5, command=print_selection)

    s.pack(side='top', expand=True)

    l = Label(frameControl, bg='white', fg='black', width=3, text='...')
    l.pack(side='top', expand=True)


for servo in servos_data:
    show_servo_scale(servo)

window.mainloop()
