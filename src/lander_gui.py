import tkinter
from PIL import Image, ImageTk
import keyboard
import threading
import four_axis_math
import serial_comm
from dataclasses import dataclass
import time

"""
defining all relevant dataclasses to represent the physical components
"""
# define a dataclass for the arduinos
@dataclass(frozen=True)
class ArduinoNano:
    port:str            # name of the COM port the arduino is connected to

# define a dataclass for the lander
@dataclass
class Lander:
    x_pos:float   # horizontal (90 deg counter-clockwise of z when looking from above)
    y_pos:float   # vertical (up is positive)
    z_pos:float   # horizontal (90 deg clockwise of x when looking from above)
    arduino:ArduinoNano

""" keep track of gravity """
gravity_const = 0

""" Instantiating the dataclasses """
# create the stepper control arduino
stepper_arduino = ArduinoNano("COM3")

# create the lander control arduino and a lander to put it in
lander_arduino = ArduinoNano("COM5")
model_lander = Lander(36, 0, 36, lander_arduino)

""" Globals """
background_color = "#001e21"
foreground_color = "#001e21"
button_x_padding = 5
button_y_padding = 5

""" Root Window """
root = tkinter.Tk()                                                                             # initialize root window
root.title("Lander")                                                                            # set window name
root.attributes('-fullscreen', True)                                                            # set size to fullscreen
root.configure(background=background_color)

""" Button Frame """
button_frame = tkinter.Frame(root)                                                              # initialize button frame
button_frame.pack(side=tkinter.BOTTOM, padx=20, pady=50)
button_frame.configure(background=background_color)

""" Button Configure """
keys = ["q", "w", "a", "s", "d", "space", "Left", "Right", "Up", "Down"]                        # define accepted input keys
register_keys = ["q", "w", "a", "s", "d", "space", "left", "right", "up", "down"]               # define accepted input keys
buttons = []                                                                                    # button array to store buttons
button_pos = [[1, 1], [1, 2], [2, 1], [2, 2], [2, 3], [3, 4], [2, 5], [2, 7], [1, 6], [2, 6]]   # button positions
key_image = ["../images/q.png", "../images/w.png", "../images/a.png", "../images/s.png", "../images/d.png", "../images/space.png", "../images/left.png", "../images/right.png", "../images/up.png", "../images/down.png"]
button_image = []
pressed_keys = set()

""" Visual Feedback: Button sunken while held, raise on release. """
def key_function(key):
    buttons[keys.index(key)].config(relief=tkinter.SUNKEN)
    root.bind("<KeyRelease-" + key + ">", lambda release_key: buttons[keys.index(key)].config(relief=tkinter.RAISED))

""" Generate Buttons """
for key in keys:
    button_image.append(ImageTk.PhotoImage(Image.open(key_image[keys.index(key)])))
    buttons.append(tkinter.Button(button_frame, image=button_image[-1], bg=background_color, fg=foreground_color))
    buttons[-1].grid(row=button_pos[keys.index(key)][0], column=button_pos[keys.index(key)][1], padx=button_x_padding, pady=button_y_padding)
    root.after(0, lambda k=key: root.bind("<" + k + ">", lambda event: key_function(k)))
    # keyboard.on_press_key(key, lambda event, k=key: key_function(k))
    # keyboard.on_release_key(key, lambda event, k=key: key_release_function(k))

""" Quit Key: Terminate program on call. """
def quit(function_call):
    exit(0)
root.bind("<Escape>", quit)

""" Keyboard Reader Function """
# this function is being hijacked as the main loop bc idk how to python
def keyboard_reader():
    while(True):
        """ ensure the lander is constantly moving down """
        do_gravity()

        """ monitors changes in which keys are down/up """
        event = keyboard.read_event()
        if event.event_type == "down":
            pressed_keys.add(event.name)    # if the key is down, add it to the set of pressed keys
        elif event.event_type == "up":
            if event.name in pressed_keys:  # if the key is up, and in the list of pressed keys, remove it
                pressed_keys.remove(event.name)

        """ iterate through the currently pressed keys, and perform the according actions """
        for key in pressed_keys:
            # send key inputs only if the key is in the keys array
            if key in register_keys:
                # TODO: switch statement to call unique functions for each key
                print(key)

        """ with all changes complete for this iteration, now physically move the lander """
        # get the list of instructions to send to the stepper motor serial port

        # send the instructions to the stepper motor serial port


def move_lander(x_change:int, y_change:int, z_change:int):
    """
    Moves the lander to the new position, as a result of user input
    :param x_change: change in x coordinate
    :param y_change: change in y coordinate
    :param z_change: change in z coordinate
    :return: none
    """
    # TODO
    return

def do_gravity():
    global gravity_const
    move_lander(0,-(gravity_const),0)
    if(gravity_const < 4):
        gravity_const += 0.1

def main():
    """ Launch GUI & Thread Keyboard Reader """
    threading.Thread(target=keyboard_reader, daemon=True).start()
    threading.Thread(target=do_gravity, daemon=True).start()
    root.mainloop()

if __name__ == '__main__':
    main()