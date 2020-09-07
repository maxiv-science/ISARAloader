import os
import time
from laser.views.dewar_load import get_dewar_status


def get_next_empty_placeholder(active, shipments, sampleChanger_position, dumps):

    if os.path.exists("static/unsafe_positions.txt"):
        with open("static/unsafe_positions.txt", "r") as readFile:
            r = readFile.read()
        r = r.replace("checked", "1")
        r = r.replace("false", "0")
        disabled_position = r.split(",")
        disabled_position = list(map(int, disabled_position))

    else:
        disabled_position = []
    # Creates dewar:status dictionary from available shipments
    inUse_position = list()
    dewars_status = {x: get_dewar_status(dumps, x) for x in shipments.keys()}
    for key, value in dewars_status.items():
        if value == "processing":
            for k, v in shipments[key].items():
                if type(sampleChanger_position[k]) is str and sampleChanger_position[k] != "Dry shipper":
                    inUse_position.append(sampleChanger_position[k])

    inUse_position = list(filter(lambda a: a != "", inUse_position))
    inUse_position = list(map(int, inUse_position))

    # print(disabled_position)
    for n, i in enumerate(active):
        if i == 1:
            inUse_position.append(n + 1)
    # inUse_position=inUse_position+disabled_position
    # dewar_pos=list(range(1,30))
    # n_empty=list(set(dewar_pos)-set(inUse_position))[0]

    # List of positions assigned in the current session
    # If the puck was assigned but not place in the sample changer, this will avoid
    # double assigning
    session_assingned = [dump["sampleChangerLocation"] for dump in dumps if dump["containerStatus"] == "processing"]
    session_assingned = [int(x) for x in session_assingned if x != "" and x is not None]

    isara_sc = dict()
    for n, i in enumerate(active, 1):
        if i == 0:
            isara_sc[n] = "free"
        else:
            isara_sc[n] = "in_use"
    for n, i in enumerate(disabled_position, 1):
        if i == 0:
            isara_sc[n] = "in_use"
    for i in inUse_position:
        isara_sc[i] = "in_use"
    for i in session_assingned:
        isara_sc[i] = "in_use"
    for pos, status in isara_sc.items():
        if status == "free":
            n_empty = pos
            break

    print("isara_sc:", isara_sc)
    print("n_empty: ", n_empty)
    print(time.ctime())
    return n_empty


def get_puck_states(ISARA_pos):
    if "None" not in ISARA_pos:
        with open("static/unsafe_positions.txt", "w") as writeFile:
            ISARA_pos = ISARA_pos.replace("true", "checked")
            writeFile.write(ISARA_pos)

    if os.path.exists("static/unsafe_positions.txt"):
        with open("static/unsafe_positions.txt", "r") as readfile:
            position_state = readfile.readlines()[0].split(",")

        state1 = position_state[0]
        state2 = position_state[1]
        state3 = position_state[2]
        state4 = position_state[3]
        state5 = position_state[4]
        state6 = position_state[5]
        state7 = position_state[6]
        state8 = position_state[7]
        state9 = position_state[8]
        state10 = position_state[9]
        state11 = position_state[10]
        state12 = position_state[11]
        state13 = position_state[12]
        state14 = position_state[13]
        state15 = position_state[14]
        state16 = position_state[15]
        state17 = position_state[16]
        state18 = position_state[17]
        state19 = position_state[18]
        state20 = position_state[19]
        state21 = position_state[20]
        state22 = position_state[21]
        state23 = position_state[22]
        state24 = position_state[23]
        state25 = position_state[24]
        state26 = position_state[25]
        state27 = position_state[26]
        state28 = position_state[27]
        state29 = position_state[28]
    else:
        state1 = "checked"
        state2 = "checked"
        state3 = "checked"
        state4 = "checked"
        state5 = "checked"
        state6 = "checked"
        state7 = "checked"
        state8 = "checked"
        state9 = "checked"
        state10 = "checked"
        state11 = "checked"
        state12 = "checked"
        state13 = "checked"
        state14 = "checked"
        state15 = "checked"
        state16 = "checked"
        state17 = "checked"
        state18 = "checked"
        state19 = "checked"
        state20 = "checked"
        state21 = "checked"
        state22 = "checked"
        state23 = "checked"
        state24 = "checked"
        state25 = "checked"
        state26 = "checked"
        state27 = "checked"
        state28 = "checked"
        state29 = "checked"
    return {
        "state1": state1,
        "state2": state2,
        "state3": state3,
        "state4": state4,
        "state5": state5,
        "state6": state6,
        "state7": state7,
        "state8": state8,
        "state9": state9,
        "state10": state10,
        "state11": state11,
        "state12": state12,
        "state13": state13,
        "state14": state14,
        "state15": state15,
        "state16": state16,
        "state17": state17,
        "state18": state18,
        "state19": state19,
        "state20": state20,
        "state21": state21,
        "state22": state22,
        "state23": state23,
        "state24": state24,
        "state25": state25,
        "state26": state26,
        "state27": state27,
        "state28": state28,
        "state29": state29,
    }
