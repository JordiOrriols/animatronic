import tkinter as tk
 
window = tk.Tk()
window.title('Calibrate Phonemes')
window.geometry('500x300') 

def show_servo_scale(servo: int):
    l = tk.Label(window, bg='white', fg='black', width=20, text='Waiting')
    l.pack()
    
    def print_selection(v):
        l.config(text=v)

    label = 'Servo ' + servo
    s = tk.Scale(window, label=label, from_=0, to=10, length=200, showvalue=0, tickinterval=2, resolution=0.01, command=print_selection)
    s.pack()
 
show_servo_scale(0)

window.mainloop()