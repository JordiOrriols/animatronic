import tkinter as tk
from common.config import servos_data
from common.validators import validate_controllable_servo

window = tk.Tk()
window.title('Calibrate Phonemes')
window.geometry('1000x300')


def show_servo_scale(servo: int, min: int, max: int):
    
    l = tk.Label(window, bg='white', fg='black', width=3, text='...')
    l.pack(side='left')

    def print_selection(v):
        l.config(text=v)

    label = '#' + str(servo)
    s = tk.Scale(window, label=label, from_=min, to=max, length=200,
                 showvalue=0, tickinterval=2, resolution=5, command=print_selection)

    s.pack(side='left')


for i in range(len(servos_data)):

    if validate_controllable_servo(i) == False:
        continue

    min = servos_data[i]['physical_limits']['min']
    max = servos_data[i]['physical_limits']['max']
    show_servo_scale(i, min, max)

window.mainloop()
