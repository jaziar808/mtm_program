# Import modules
import serial
import serial.tools.list_ports
from time import sleep

STEPPER_PORT = 'COM5'
LANDER_PORT = 'COM3'

# Print out existing ports for reference
available = [i.device for i in list(serial.tools.list_ports.comports())]
print(f'Available ports: {", ".join(available)}')
'''
try:
    lander = serial.Serial(LANDER_PORT, 115200, timeout=0.1)
except Exception as err:
    lander = None
    print('Failed to connect to lander!')
    print(err)
try:
    stepper = serial.Serial(STEPPER_PORT, 115200, timeout=0.1)
except Exception as err:
    print('Failed to connect to stepper!')
    print(err)

sleep(4)'''


def get_image() -> bytes:
    """
    Tells the lander to give us an image
    """
    # Send the command
    lander.write(bytes([0x10]))

    # Read results
    reading = True
    msg = b''
    while reading:
        # Read data
        try:
            msg += lander.readline()
        except:
            return b''
        # Found end-of-file
        if len(msg) > 0:
            if msg[-2:] == b'\xff\xd9':
                reading = False

        # Pause thread
        sleep(0)

    # Find start of image
    start_index = msg.find(b'\xff\xd8')
    msg = msg[start_index:]

    # Return result
    return msg


def get_distance() -> int:
    """
    Ask the lander if we're too close to the ground
    """
    # Send the command
    lander.write(bytes([0x73]))

    # Read results
    reading = True
    msg = b''
    while reading:
        # Read data
        try:
            msg += lander.readline()
        except:
            return False

        # Done reading
        if len(msg) > 0:
            reading = False

        # Pause thread
        sleep(0)

    # Return message status
    return int(msg)


def write_to_stepper(instructions:bytes):
    stepper.write(instructions)