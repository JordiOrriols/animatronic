import tkinter as tk
from common.config import servos_data
 
window = tk.Tk()
window.title('Calibrate Phonemes')
window.geometry('800x400') 

def show_servo_scale(servo: int, min: int, max: int):
    l = tk.Label(window, bg='white', fg='black', width=3, text='...')
    l.pack()
    
    def print_selection(v):
        l.config(text=v)

    label = 'S#' + str(servo)
    s = tk.Scale(window, label=label, from_=min, to=max, length=200, showvalue=0, tickinterval=2, resolution=5, command=print_selection)
    
    s.pack(side = 'left', padx = 5)

for i in range(len(servos_data)):

    if servos_data[i]['type'] == 'disabled':
        continue

    show_servo_scale(i, servos_data[i]['physical_limits']['min'], servos_data[i]['physical_limits']['max'])

window.mainloop()