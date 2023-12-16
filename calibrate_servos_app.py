from tkinter import Tk, Frame, Scale, Label

from common.servo import AniServo
from common.project import Project

# Initialization
project = Project()

window = Tk()
window.title("Calibrate Animatronic")
window.geometry("850x300")

# Run code


def show_servo_scale(servo: AniServo):
    frameControl = Frame(window)
    frameControl.pack(side="left", padx=10)

    label = "#" + str(servo.get_pin())
    n = Label(frameControl, fg="black", width=3, text=label)
    n.pack(side="top", expand=True)

    def print_selection(v):
        l.config(text=v)
        servo.move_to_angle(int(v))

    s = Scale(
        frameControl,
        from_=servo.get_physical_limit_min(),
        to=servo.get_physical_limit_max(),
        length=200,
        showvalue=0,
        tickinterval=2,
        resolution=5,
        command=print_selection,
    )

    s.set(servo.get_rest_position())
    s.pack(side="top", expand=True)

    l = Label(frameControl, bg="white", fg="black", width=3, text="...")
    l.pack(side="top", expand=True)


for servo in project.get_servos_data():
    show_servo_scale(servo)

window.mainloop()
