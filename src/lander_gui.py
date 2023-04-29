import tkinter
from PIL import Image, ImageTk
import keyboard
import threading
from four_axis_math import *
from serial_comm import get_image, is_in_danger, write_to_stepper
from dataclasses import dataclass
import time
from io import BytesIO
from time import sleep

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
model_lander = Lander(34, 4.5, 32.5, lander_arduino)

""" Globals """
background_color = "#001e21"
foreground_color = "#001e21"
button_x_padding = 5
button_y_padding = 5
image_width = 120*4
image_height = 120*4

""" Root Window """
root = tkinter.Tk()                                                                             # initialize root window
root.title("Lander")                                                                            # set window name
root.attributes('-fullscreen', True)                                                            # set size to fullscreen
root.configure(background=background_color)

""" Title """
title_label = tkinter.Label(root, width=50, height=1, font=('Consolas', 32), text='Mission Control')
title_label.pack(side=tkinter.TOP)
title_label.configure(background=background_color, foreground='white')

""" Canvas """
canvas = tkinter.Canvas(root, width=image_width, height=image_height)
canvas.pack(side=tkinter.TOP, padx=20, pady=0)
canvas.configure(background=background_color)

""" Button Frame """
button_frame = tkinter.Frame(root)                                                              # initialize button frame
button_frame.pack(side=tkinter.BOTTOM, padx=20, pady=8)
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
        """ store the initial position of the lander """
        x_current = model_lander.x_pos
        y_current = model_lander.y_pos
        z_current = model_lander.z_pos

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
                if key == "q":
                    pass
                if key == "w":
                    model_lander.x_pos = (model_lander.x_pos + 0.1)
                if key == "a":
                    model_lander.z_pos = (model_lander.z_pos - 0.1)
                if key == "s":
                    model_lander.x_pos = (model_lander.x_pos - 0.1)
                if key == "d":
                    model_lander.z_pos = (model_lander.z_pos + 0.1)
                if key == "space":
                    model_lander.y_pos = (model_lander.y_pos + 0.1)
                    global gravity_const
                    gravity_const = gravity_const - 0.2
                if key == "left":
                    pass
                if key == "right":
                    pass
                if key == "up":
                    pass
                if key == "down":
                    pass
                print(key)

                # check to ensure that all coordinates are valid and not too close to the ground/edges
                if model_lander.x_pos > 62:
                    model_lander.x_pos = 62
                if model_lander.x_pos < 6:
                    model_lander.x_pos = 6
                if model_lander.z_pos > 59:
                    model_lander.z_pos = 59
                if model_lander.z_pos < 6:
                    model_lander.z_pos = 6
                if model_lander.y_pos < 4:
                    model_lander.y_pos = 4
                if model_lander.y_pos > 36:
                    model_lander.y_pos = 36

                # check to make sure gravity isn't negative
                if gravity_const < 0:
                    gravity_const = 0

        """ with all changes complete for this iteration, now physically move the lander """
        # current pos is the values that were stored at the beginning of the loop
        # target pos is the values of the fields in the model_lander dataclass, which (may) have been changed
        move_lander(x_current, y_current, z_current, model_lander.x_pos, model_lander.y_pos, model_lander.z_pos)

        # Pause thread
        sleep(0)

def move_lander(x_current:float, y_current:float, z_current:float,
                x_target:float, y_target:float, z_target:float):
    """
    Generates instructions and sends them to the arduino to physically move the lander
    :param x_current: the current x position of the lander
    :param y_current: the current y position of the lander
    :param z_current: the current z position of the lander
    :param x_target: the target x position of the lander
    :param y_target: the target y position of the lander
    :param z_target: the target z position of the lander
    :return: none
    """

    # get the byte list using the function in four_axis_math.py
    byte_list = get_byte_list(x_current, y_current, z_current, x_target, y_target, z_target)

    # send the instructions to the serial port, using the method that is defined in serial_comm.py
    write_to_stepper(byte_list)
    return

def do_gravity():
    global gravity_const
    # move the lander down
    model_lander.y_pos = (model_lander.y_pos - gravity_const)

    # check to make sure the lander height is valid
    if(model_lander.y_pos < 4.5):
        model_lander.y_pos = 4.5

    # increase the gravity const
    if(gravity_const < 0.5):
        gravity_const += 0.1

_canvas_image = None  # Necessary to prevent image from being garbage-collected
def bytes_to_canvas(image_bytes: bytes):
    """Pushes the received sequence of bytes to the canvas"""
    global canvas
    global _canvas_image
    # Convert bytes string to PhotoImage
    img = Image.open(BytesIO(image_bytes))
    img = img.rotate(90)
    # Resize image to fit canvas
    scale_factor = image_height/ img.height
    img = img.resize((int(img.width*scale_factor), int(img.height*scale_factor)))

    # Convert image to tkinter-compatible PhotoImage and save to global scope
    image = ImageTk.PhotoImage(img)
    _canvas_image = image

    # Clear canvas, push the new image, and tell it to reload
    canvas.delete('all')
    canvas.create_image((image_width/2, image_height/2), image=image)  # Note: placement coordinates anchored to center of image
    canvas.update()

def lander_thread_function():
    """Lander thread stuff"""
    while True:
        # Grab image data and push to canvas
        print('check')
        image = get_image()
        print('Got:', len(image))
        bytes_to_canvas(image)

        # Grab danger status
        danger = is_in_danger()
        if danger:
            print("STOOOOOOOOOOP")

def main():
    """ Launch GUI & Thread Keyboard Reader """
    thd1 = threading.Thread(target=keyboard_reader, daemon=True).start()
    thd2 = threading.Thread(target=lander_thread_function, daemon=True).start()
    root.mainloop()

if __name__ == '__main__':
    main()