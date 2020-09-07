from RpiMotorLib import rpi_pservo_lib
import pickle
from os import path

laser_servo = rpi_pservo_lib.ServoPigpio("Sone", 50, 1000, 2000)


def SetAngle_tilt(duty):
    # duty = laser_servo.convert_from_degree(ang)
    laser_servo.servo_move(17, duty, 0.5, False, 0.01)
    print("Move to " + str(duty))


def SetAngle_pan(duty):
    # New servo not yet defined
    laser_servo.servo_move(26, duty, 0.5, False, 0.01)
    print("Move to " + str(duty))


def reset_all_baskets():
    return {
        1: {"tilt": 1700, "pan": 1500},
        2: {"tilt": 1800, "pan": 1500},
        3: {"tilt": 1400, "pan": 1500},
        4: {"tilt": 1300, "pan": 1500},
        5: {"tilt": 1450, "pan": 1500},
        6: {"tilt": 1550, "pan": 1500},
        7: {"tilt": 1500, "pan": 1500},
        8: {"tilt": 1500, "pan": 1500},
        9: {"tilt": 1500, "pan": 1500},
        10: {"tilt": 1500, "pan": 1500},
        11: {"tilt": 1500, "pan": 1500},
        12: {"tilt": 1500, "pan": 1500},
        13: {"tilt": 1500, "pan": 1500},
        14: {"tilt": 1500, "pan": 1500},
        15: {"tilt": 1500, "pan": 1500},
        16: {"tilt": 1500, "pan": 1500},
        17: {"tilt": 1500, "pan": 1500},
        18: {"tilt": 1500, "pan": 1500},
        19: {"tilt": 1500, "pan": 1500},
        20: {"tilt": 1500, "pan": 1500},
        21: {"tilt": 1500, "pan": 1500},
        22: {"tilt": 1500, "pan": 1500},
        23: {"tilt": 1500, "pan": 1500},
        24: {"tilt": 1500, "pan": 1500},
        25: {"tilt": 1500, "pan": 1500},
        26: {"tilt": 1500, "pan": 1500},
        27: {"tilt": 1500, "pan": 1500},
        28: {"tilt": 1500, "pan": 1500},
        29: {"tilt": 1500, "pan": 1500},
    }


def get_baskets_positions():
    if path.exists("/home/pi/baskets.pickle"):
        with open("/home/pi/baskets.pickle", "rb") as pickle_file:
            baskets = pickle.load(pickle_file)
    else:
        baskets = reset_all_baskets()
    return baskets
