import tkinter
from PIL import Image, ImageTk
import keyboard
import threading
from four_axis_math import *
from s_comm import get_image, get_distance, write_to_stepper
from dataclasses import dataclass
import time
from io import BytesIO
from time import sleep

sensor_distance = 0

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

""" Distance display """
distance_label = tkinter.Label(root, font=('Consolas', 20), text=sensor_distance)
distance_label.pack(side=tkinter.TOP)

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
    grav_on = False

    while(True):
        """ ensure the lander is constantly moving down """
        if grav_on:
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
                    write_to_stepper(b'\x31\x32\x33\x34')
                if key == "w":
                    write_to_stepper(b'\x32\x33')
                if key == "a":
                    write_to_stepper(b'\x33\x34')
                if key == "s":
                    write_to_stepper(b'\x31\x34')
                if key == "d":
                    write_to_stepper(b'\x31\x32')
                if key == "space":
                    write_to_stepper(b'\x61\x62\x43\x64\x35')
                if key == "up":
                    write_to_stepper(b'\x33')
                if key == "right":
                    write_to_stepper(b'\x32')
                if key == "down":
                    write_to_stepper(b'\x31')
                if key == "left":
                    write_to_stepper(b'\x34')
                print(key)

        # Pause thread
        sleep(0)

def do_gravity():
    global gravity_const
    # move the lander down
    # write_to_stepper(b'\x41\x42\x43\x44\x31\x32\x33\x34')

    # check to make sure the lander height is valid
    #if(model_lander.y_pos < 4.5):
    #    model_lander.y_pos = 4.5

    # increase the gravity const
    #if(gravity_const < 2):
    #    gravity_const += 0.1

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
        image = get_image()
        bytes_to_canvas(image)

        # Grab danger status
        sensor_distance = get_distance()

def main():
    """ Launch GUI & Thread Keyboard Reader """
    thd1 = threading.Thread(target=keyboard_reader, daemon=True).start()
    thd2 = threading.Thread(target=lander_thread_function, daemon=True).start()
    root.mainloop()

if __name__ == '__main__':
    main()