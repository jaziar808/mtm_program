import math

def convert_num_steps_to_bytes(num_steps:list)->str:
    # initialize byte string
    byte_str = ""

    # TODO: dont worry about this nic ill do it - it kinda depends on how the motors are physically mounted and how the arduino code works, so it would just be confusing

    return byte_str

def distance_to_num_steps(distance:int)->list:
    """
    Used to convert a distance to degrees of rotation
    :param distance: the desired distance
    :return: degrees of rotation necessary to change length by the desired distance
    """
    # initialize a list
    steps_list = []

    # TODO: first convert from change in length to degrees of rotation - assume radius is 1 (might change once i actually measure the pulley)

    # TODO: second, convert from degrees of rotation to number of steps (1 step is 0.9 degrees - so a change of 90 degrees is 100 steps)

    # index 0 should be the number of steps for motor 1, index 1 should be the number of steps for motor 2, etc.
    return steps_list

def get_lengths(x:float,y:float,z:float)->list:
    """
    Used to calculate the lengths of the four physical strings for some point in 3D
    :param x: the x value of the point
    :param y: the y value of the point
    :param z: the z value of the point
    :return: list of length 4, with the lengths of the four strings
    """
    #initialize a list
    lengths_list = []

    # TODO: populate the list with the length of all four strings (motor 1 at index 0, motor 2 at index 1, etc.)
    # NOTE: motor 1 is at the intersection of the x, y, and z axes, flush with the floor
    #       when looking down from above, motors 2, 3, and 4 are then located in each corner when
    #       going clockwise from motor 1, in order
    #       all motors are located 72 inches above the ground - btw all of these units are just inches
    #       imagine the frame as a 72 x 72 x 72 inch cube, with the motors at each top corner
    #       then calculate the lengths based off of that


    return lengths_list

def get_byte_list(x_pos_current:float, y_pos_current:float, z_pos_current:float, x_pos_target:float, y_pos_target:float, z_pos_target:float)->str:
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
    # NOTE: THESE VALUES CAN BE NEGATIVE, AND SHOULD BE LEFT THAT WAY IF SO
    length_differences = [] # TODO: instead of an empty list, it should be a list of length 4 with the differences

    # translate change in length to number of steps for each motor
    # NOTE: THESE VALUES CAN BE NEGATIVE, AND SHOULD BE LEFT THAT WAY IF SO
    num_steps = [] # TODO: use a for loop to iterate through the "length_differences" list, and call distance_to_num_steps() for each one

    # create a string representing the instructions as a sequence of bytes
    byte_list = convert_num_steps_to_bytes(num_steps)

    # TODO: returns an empty string at the moment
    return byte_list