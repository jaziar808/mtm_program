import math

# defined bytes to step the motors
STEP_ARR = [b'\x31',b'\x32',b'\x33',b'\x34']

# defined bytes to set motors' directions - index 0 is motor 1, etc.
DIR_EXTEND_ARR = [b'\x41',b'\x42',b'\x43',b'\x44']
DIR_RETRACT_ARR = [b'\x61',b'\x62',b'\x63',b'\x64']

def convert_num_steps_to_bytes(num_steps: list) -> bytes:
    # initialize byte string
    byte_str = b''

    # first four bytes should specify the direction for each of the four motors
    for i in range(4):
        if num_steps[i] < 0:
            byte_str += DIR_RETRACT_ARR[i]
            num_steps[i] = (num_steps[i] * -1)  # ensures that all values in num_steps are positive after this loop
        elif num_steps[i] > 0:
            byte_str += DIR_EXTEND_ARR[i]

    """ now insert the step bytes for each motor into the byte_str - previous loop made all values positive
        currently inserts instructions by adding instructions for the motors with the most steps first """
    # store the total number of instructions to write
    tot_instr = num_steps[0] + num_steps[1] + num_steps[2] + num_steps[3]

    # iterate for the number of total instructions
    for i in range(tot_instr):
        # determine the highest number of steps
        target = max(num_steps[0],num_steps[1],num_steps[2],num_steps[3])

        # find the part of the array with that highest number
        for k in range(4):
            if num_steps[k] == target:
                num_steps[k] = (num_steps[k] - 1)   # decrease the value in the array
                byte_str += STEP_ARR[k]             # add the command to the byte string
                break

    return byte_str


def distance_to_num_steps(distances:list) -> list:
    """
    Used to convert a list of distances to degrees of rotation
    :param distance: the desired distance
    :return: degrees of rotation necessary to change length by the desired distance
    """
    # initialize a list
    steps_list = []

    # index 0 should be the number of steps for motor 1, index 1 should be the number of steps for motor 2, etc.

    # Documentation: let s be arc on circle, r be radius
    # s = 2 pi r (angle / 360)
    # angle = (180 s)/(pi r)
    # r = 0.19
    # 1 step = .9 degrees
    # steps = (200 s)/(pi r)
    steps_list[0] = ((200 * distances[0]) / (math.pi * 0.19)) (int)
    steps_list[1] = ((200 * distances[1]) / (math.pi * 0.19)) (int)
    steps_list[2] = ((200 * distances[2]) / (math.pi * 0.19)) (int)
    steps_list[3] = ((200 * distances[3]) / (math.pi * 0.19)) (int)

    # MULTIPLY ALL VALUES BY TWO - THIS ACCOUNTS FOR THE FACT THAT THE STRINGS ARE NOW MOUNTED AS "PULLEYS"
    # THIS SHOULD BE REMOVED ONLY IF THE STRINGS ARE DIRECTLY PULLING THE LANDER
    for i in range(4):
        steps_list[i] = (steps_list[i] * 2)

    return steps_list


def get_lengths(x: float, y: float, z: float) -> list:
    """
    Used to calculate the lengths of the four physical strings for some point in 3D
    :param x: the x value of the point
    :param y: the y value of the point
    :param z: the z value of the point
    :return: list of length 4, with the lengths of the four strings
    """
    # initialize a list
    lengths_list = []

    # TODO: populate the list with the length of all four strings (motor 1 at index 0, motor 2 at index 1, etc.)
    # NOTE: motor 1 is at the intersection of the x, y, and z axes, flush with the floor
    #       when looking down from above, motors 2, 3, and 4 are then located in each corner when
    #       going clockwise from motor 1, in order
    #       all motors are located 72 inches above the ground - all units are in inches
    #       the frame is a 68 x 72 x 65 inch rectangle, with the motors at each top corner

    # Documentation to make sure I didn't screw up lol
    # Motor 1 is at <0,72,0>
    # Motor 2 is at <0,72,65>
    # Motor 3 is at <68,72,65>
    # Motor 4 is at <68,72,0>
    lengths_list[0] = math.sqrt(x ^ 2 + (72 - y) ^ 2 + z ^ 2)
    lengths_list[1] = math.sqrt(x ^ 2 + (72 - y) ^ 2 + (65 - z) ^ 2)
    lengths_list[2] = math.sqrt((72 - x) ^ 2 + (72 - y) ^ 2 + (72 - z) ^ 2)
    lengths_list[3] = math.sqrt((72 - x) ^ 2 + (72 - y) ^ 2 +   z ^ 2)

    return lengths_list


def get_byte_list(x_pos_current: float, y_pos_current: float, z_pos_current: float,
                  x_pos_target: float, y_pos_target: float, z_pos_target: float) -> str:
    """
    Creates a list of bytes that represent instructions for the stepper motors
    :param x_pos_current: current x position of the lander
    :param y_pos_current: current y position of the lander
    :param z_pos_current: current z position of the lander
    :param x_pos_target: target x position of the lander
    :param y_pos_target: target y position of the lander
    :param z_pos_target: target z position of the lander
    :return: list of byte instructions to move the motors
    """

    # get a list of current lengths
    current_lengths = get_lengths(x_pos_current, y_pos_current, z_pos_current)

    # get a list of desired lengths
    target_lengths = get_lengths(x_pos_target, y_pos_target, z_pos_target)

    # calculate the difference in length for each one
    length_differences = []
    length_differences[0] = target_lengths[0] - current_lengths[0]
    length_differences[1] = target_lengths[1] - current_lengths[1]
    length_differences[2] = target_lengths[2] - current_lengths[2]
    length_differences[3] = target_lengths[3] - current_lengths[3]

    # translate change in length to number of steps for each motor
    num_steps = distance_to_num_steps(length_differences)

    # create a string representing the instructions as a sequence of bytes
    byte_list = convert_num_steps_to_bytes(num_steps)
    # TODO: returns empty at the moment
    return byte_list