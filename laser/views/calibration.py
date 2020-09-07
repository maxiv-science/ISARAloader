import curses
from time import sleep
import pickle
from os import path
from servo import SetAngle_tilt, SetAngle_pan, reset_all_baskets

# https://github.com/gavinlyonsrepo/RpiMotorLib/blob/master/Documentation/Servo_pigpio.md
# SG90 http://www.ee.ic.ac.uk/pcheung/teaching/DE1_EE/stores/sg90_datasheet.pdf
# https://i.ytimg.com/vi/HeTAmc_aT4g/maxresdefault.jpg


def main(stdscr):
    if path.exists("/home/pi/baskets.pickle"):
        with open("/home/pi/baskets.pickle", "rb") as pickle_file:
            baskets = pickle.load(pickle_file)
        print(baskets)
    else:
        baskets = reset_all_baskets()

    current = {"pos": 1}

    def reset_basket():
        basket_n = current["pos"]
        baskets[basket_n]["tilt"] = 1500
        baskets[basket_n]["pan"] = 1500
        SetAngle_tilt(baskets[basket_n]["tilt"])
        # SetAngle_pan(baskets[basket_n]["pan"])

    def move_up():
        basket_n = current["pos"]
        print(f"moving up - basket {basket_n}")
        print(baskets[basket_n]["tilt"])
        baskets[basket_n]["tilt"] += 5
        SetAngle_tilt(baskets[basket_n]["tilt"])

    def move_up_half():
        basket_n = current["pos"]
        print(f"moving up - basket {basket_n}")
        print(baskets[basket_n]["tilt"])
        baskets[basket_n]["tilt"] += 1
        SetAngle_tilt(baskets[basket_n]["tilt"])

    def move_down():
        basket_n = current["pos"]

        print("moving down")
        print(baskets[basket_n]["tilt"])
        baskets[basket_n]["tilt"] -= 5
        SetAngle_tilt(baskets[basket_n]["tilt"])

    def move_down_half():
        basket_n = current["pos"]
        print("moving down")
        print(baskets[basket_n]["tilt"])
        baskets[basket_n]["tilt"] -= 1
        SetAngle_tilt(baskets[basket_n]["tilt"])

    def re_move():
        basket_n = current["pos"]
        SetAngle_tilt(1000)
        sleep(0.5)
        SetAngle_tilt(baskets[basket_n]["tilt"])

        # SetAngle_pan(tilt_pan["pan"])

    def move_left():
        print("moving left")

    def move_right():
        print("moving right")

    def next_basket():
        current["pos"] += 1

        if current["pos"] == 5:
            current["pos"] = 1
        cp = current["pos"]
        re_move()
        print(f"Current basket {cp}")

    def previous_basket():
        current["pos"] -= 1
        if current["pos"] == 0:
            current["pos"] = 4
        cp = current["pos"]
        re_move()
        print(f"Current basket {cp}")

    def save_tilt_pan():
        print("Saving tilt and pan values for current basket")

        with open("/home/pi/baskets.pickle", "wb") as writeFile:
            pickle.dump(baskets, writeFile)

    # do not wait for input when calling getch
    stdscr.nodelay(1)
    basket_n = current["pos"]
    print(f"Current basket {basket_n}")
    SetAngle_tilt(baskets[basket_n]["tilt"])
    # SetAngle_pan(baskets[basket_n]["pan"])
    while True:
        # get keyboard input, returns -1 if none available
        c = stdscr.getch()
        if c != -1:
            # print numeric value
            # stdscr.addstr(str(c) + " ")
            stdscr.addstr(str(c) + " ")
            stdscr.refresh()
            if c == 56:  # kp 8
                move_up_half()
            if c == 50:  # kp 2
                move_down_half()
            if c == 259:  # up
                move_up()
            if c == 258:  # down
                move_down()
            if c == 260:  # left
                move_left()
            if c == 261:  # right
                move_right()
            if c == 110:  # n
                next_basket()
            if c == 112:  # p
                previous_basket()
            if c == 115:  # s
                save_tilt_pan()
            if c == 32:  # spacebar
                re_move()
            if c == 114:  # r
                print("Reseting position to 90,90")
                reset_basket()

            if c == 27:  # ESC
                print("Exiting")
                print("Stopping all GPIO communication")
                sleep(0.3)
                break
            # return curser to start position
            stdscr.move(0, 0)


if __name__ == "__main__":
    curses.wrapper(main)
