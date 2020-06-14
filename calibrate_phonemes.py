import tkinter as tk
from common.config import servos_data
 
window = tk.Tk()
window.title('Calibrate Phonemes')
window.geometry('800x600') 

def show_servo_scale(servo: int):
    l = tk.Label(window, bg='white', fg='black', width=20, text='Waiting')
    l.pack()
    
    def print_selection(v):
        l.config(text=v)

    label = 'Servo ' + str(servo)
    s = tk.Scale(window, label=label, from_=0, to=100, length=200, showvalue=0, tickinterval=2, resolution=5, command=print_selection)
    s.pack()

for i in range(len(servos_data)):

    if servos_data[i]['type'] == 'disabled':
        continue

    show_servo_scale(0)

window.mainloop()