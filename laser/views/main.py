from django.shortcuts import render
import requests
import os
import time

from laser.views.staff import staff_list
from laser.views.auth import authenticate, check_token, url, site, proxies
from laser.views.proposals import get_staff_all_proposals, get_proposals
from laser.views.ISARA import get_puck_states, get_next_empty_placeholder
from laser.views.servo import SetAngle_tilt, get_baskets_positions  # , SetAngle_pan
from laser.views.dewar_load import (
    get_samples_in_puck,
    unload_all_pucks,
    get_pucks_in_dewar,
    update_puck_location_ISARA,
    update_dewar_status,
    get_dewar_status,
    get_shipping_names_and_Ids,
)


token = ""

baskets = get_baskets_positions()


def duo_login(request):
    message = "Please login with your DUO account"
    proposals = None
    login_state = "0"
    if os.path.exists("static/.auth/session_auth.txt"):
        login_state = "1"
        if os.path.exists("static/.auth/session_user.txt"):
            with open("static/.auth/session_user.txt") as r:
                fcontent = r.read()
            user, proposals = fcontent.split(";")
            proposals = proposals.split(",")
            with open("static/.auth/session_auth.txt", "r") as readFile:
                token = readFile.read()
                token = token.split(",")[0]

            if user in staff_list:
                proposals = get_staff_all_proposals(url, token)
            print("user, proposals" + str(fcontent))
            print(time.ctime())
        return render(
            request,
            "laser/duo_login.html",
            {"login": user, "proposals": proposals, "login_state": login_state, "message": ""},
        )
    elif request.POST.get("login") and request.POST.get("password"):
        login = request.POST.get("login")
        password = request.POST.get("password")
        session_token = authenticate(url, login, password, site, proxies)

        if not session_token:
            # checks if token exists based on login and password,
            # if not, refuses connection and ask user to try again
            login_state = "0"
            return render(
                request,
                "laser/duo_login.html",
                {
                    "login_state": login_state,
                    "login": login,
                    "password": password,
                    "message": "Wrong username and/or password",
                },
            )
        else:
            # if authentication works
            # change login state to 0
            # get list of proposals
            proposals = get_proposals(login, password)
            login_state = "1"
            token = authenticate(url, login, password, site, proxies)
            if login in staff_list:
                proposals = get_staff_all_proposals(url, token)
            # create session files with user, proposals and token
            os.makedirs("static/.auth", exist_ok=True)
            with open("static/.auth/session_auth.txt", "w") as writeFile:
                writeFile.write(token + "," + proposals[0])
            with open("static/.auth/session_user.txt", "w") as writeFile:
                writeFile.write(login + ";" + ",".join(proposals))

            return render(
                request,
                "laser/duo_login.html",
                {
                    "login_state": login_state,
                    "proposals": proposals,
                    "login": login,
                    "password": password,
                    "message": "Login OK",
                },
            )
    else:
        # starts new session if no token file is available
        login_state = "0"
        return render(request, "laser/duo_login.html", {"login_state": login_state, "message": message})


def duo_logout(request):

    login_state = "0"
    message = "You logged out"
    if os.path.exists("static/.auth/session_auth.txt"):
        os.system("rm static/.auth/session_auth.txt")
        os.system("rm static/.auth/session_user.txt")
        return render(request, "laser/duo_login.html/", {"login_state": login_state, "message": message})
    else:
        return render(request, "laser/duo_login.html/", {"login_state": login_state, "message": message})


def safe_pucks(request):
    ISARA_pos = str(request.GET.get("savebtn"))
    puck_states = get_puck_states(ISARA_pos)
    return render(request, "laser/safe_pucks.html", puck_states,)


def load_isara(request):
    print("Moving laser in ISARA...")
    print(time.ctime())
    # check for unload all pucks options
    unloadCMD = str(request.GET.get("unloadbutton"))
    user = ""
    if "unloadALL" in unloadCMD:
        if os.path.exists("static/.auth/session_auth.txt"):
            with open("static/.auth/session_auth.txt", "r") as r:
                fcontent = r.read()
            token, proposal = fcontent.split(",")
            proposal = proposal.replace("MX", "")
            response = requests.get(url + "/" + token + "/proposal/MX" + proposal + "/dewar/list")
            dumps = response.json()
            unload_all_pucks(token, proposal, dumps)

    # Tango device for ISARA
    # Read information about used positions on SC
    # Green is free, Orange is in use
    # returns a list "active" with 0s and 1s
    shipments = [""]
    pucks_in_shipment = [""]
    next_empty = ""
    puck_mounted_dict = {}
    url_jive = "https://webjive.maxiv.lu.se/biomax/db"

    q = {
        "query": '{\n  device(name: "b311a-e/ctl/cats-01") {\n    attributes(pattern:"CassettePresence") {\n        name\n      value\n}\n    }\n  }\n  '
    }

    if request.method == "POST":
        proposalID = request.POST.get("proposalID")
        proposal = proposalID
        os.makedirs("static/.auth", exist_ok=True)
        if proposalID and os.path.exists("static/.auth/session_auth.txt"):
            proposal = proposalID
            with open("static/.auth/session_auth.txt", "r") as readFile:
                token = readFile.read()
                token = token.split(",")[0]
            with open("static/.auth/session_auth.txt", "w") as writeFile:
                writeFile.write(token + "," + proposal)
        with open("static/.auth/session_proposal.txt", "w") as writeFile:
            writeFile.write(proposalID)

    if os.path.exists("static/.auth/session_auth.txt"):
        with open("static/.auth/session_auth.txt", "r") as r:
            fcontent = r.read()
        token, proposal = fcontent.split(",")
        with open("static/.auth/session_proposal.txt", "r") as r:
            fcontent = r.read()
        proposal = fcontent.split()[0]

        proposal = proposal.replace("MX", "")
        check_token(token)
        if os.path.exists("static/.auth/session_user.txt"):
            with open("static/.auth/session_user.txt") as r:
                fcontent = r.read()
            user, proposals = fcontent.split(";")
            proposals = proposals.split(",")
        else:
            proposal = ""
            token = ""
    else:
        proposal = ""
        token = ""

    puckposition = "None"
    puckposition = str(request.GET.get("puckpos"))
    print(puckposition)

    if "None" not in puckposition:
        puckposition = puckposition.replace("position", "")
        pos = int(puckposition)
        SetAngle_tilt(baskets[pos]["tilt"])
        # SetAngle_tilt(baskets[pos]["pan"])

    # out = requests.post(url_jive, data=json.dumps(q), verify=False).json()

    # active = out["data"]["device"]["attributes"][0]["value"]

    active = 10 * [0] + 7 * [1] + 2 * [0] + 10 * [1]

    activeList = list()
    for i in active:
        if i == 0:
            activeList.append("unipuck-free")
        else:
            activeList.append("unipuck-occupied")

    print("Baskets in use..")
    print("activeList", activeList)
    # ISPyB listing from available shippings and pucks
    shippingName = str(request.GET.get("select_shipment"))
    containerId = str(request.GET.get("containerId"))
    print("shippingName and containerId")
    print(shippingName, containerId)
    if token != "":
        response = requests.get(url + "/" + token + "/proposal/MX" + proposal + "/dewar/list")
        dumps = response.json()
        # Creates dictionary of dewars (shippingName/Id)
        # with values = pucks inside the dewar (containerName/Id)
        shipments = dict()
        shippingId_dict = dict()
        sampleChanger_position = dict()
        sampleChanger_positionId = dict()
        for dump in dumps:
            Id = dump["shippingId"]
            Name = dump["shippingName"]
            pucks = get_pucks_in_dewar(dumps, int(Id))
            shipments[Name] = pucks
            # Create dictionary with pucks and their assignement inside SC (ISPyB)
            # Does not filter for processing only
            sc_position = dump["sampleChangerLocation"]
            sampleChanger_position[dump["containerCode"]] = sc_position
            sampleChanger_positionId[dump["containerId"]] = sc_position
            for key, value in pucks.items():
                shippingId_dict[value] = Name

        print("shippingId_dict: ", shippingId_dict)

        if shippingName == "None":
            if containerId == "None":
                pucks_in_shipment = ""
            else:
                shippingName = shippingId_dict[int(containerId)]
                pucks_in_shipment = shipments[shippingName]

                if get_dewar_status(dumps, shippingName) != "processing":
                    shippingId = get_shipping_names_and_Ids(dumps)[shippingName]

                    update_dewar_status(url, token, proposal, shippingId, "processing")
                # print(containerId)
                SC_position = sampleChanger_positionId[int(containerId)]
                # print(SC_position)
                if SC_position == "" or SC_position == None:
                    print("Searching next available position for the puck...")
                    print(containerId)
                    # print("HERE")
                    next_empty = get_next_empty_placeholder(active, shipments, sampleChanger_position, dumps)
                    update_puck_location_ISARA(url, token, proposal, containerId, next_empty)
                    print("Next available position is ")
                    print(next_empty)
                    pos = int(next_empty)
                    SetAngle_tilt(baskets[pos]["tilt"])
                    # SetAngle_tilt(baskets[pos]["pan"])
                    # print(shippingName)
                    # print(next_empty)
                    puck_mounted_dict[containerId] = next_empty
                    print("puck_mounted_dict:", puck_mounted_dict)
                else:
                    pos = SC_position
                    try:
                        pos = int(pos)
                        SetAngle_tilt(baskets[pos]["tilt"])
                        # SetAngle_tilt(baskets[pos]["pan"])
                    except:
                        pass
        else:
            pucks_in_shipment = shipments[shippingName]
            print("pucks_in_shipment:", pucks_in_shipment)

    try:
        del pucks_in_shipment[None]
    except:
        pass
    print("After puck_in_shipment cleanup")
    print(pucks_in_shipment)
    try:
        pucks_in_shipment = shipments[shippingName]
        for key, value in pucks_in_shipment.items():
            puck_mounted_dict[value] = sampleChanger_positionId[int(value)]
    except:
        pass

    samples_in_pucks_status = list()
    sample_avail = "none"
    try:
        for i in pucks_in_shipment.values():
            st = get_samples_in_puck(url, token, proposal, str(i))
            samples_in_pucks_status.append(st)
            sample_avail = "OK"
    except:
        samples_in_pucks_status = [[containerId, "Unipuck Example"] + ["sample-empty"] * 16]
        sample_avail = "none"
    # print(pucks_in_shipment)

    # print(shipments)
    print(samples_in_pucks_status)
    userstate = "visitor"
    if user in staff_list:
        userstate = "staff"

    with open("static/unsafe_positions.txt", "r") as readfile:
        position_state = readfile.readlines()[0].split(",")
    indices = [i for i, x in enumerate(position_state) if x == "false"]
    for index_i in indices:
        activeList[index_i] = "unipuck-disabled"
    print(time.ctime())
    return render(
        request,
        "laser/isara.html",
        {
            "userstate": user,
            "proposal": proposal,
            "shipments": shipments,
            "select_shipment": shippingName,
            "pucks_in_shipment": pucks_in_shipment,
            "puck_mounted_dict": puck_mounted_dict,
            "samples_in_pucks_status": samples_in_pucks_status,
            "containerId": containerId,
            "sample_avail": sample_avail,
            "next_empty": next_empty,
            "active": activeList,
            "status1": activeList[0],
            "status2": activeList[1],
            "status3": activeList[2],
            "status4": activeList[3],
            "status5": activeList[4],
            "status6": activeList[5],
            "status7": activeList[6],
            "status8": activeList[7],
            "status9": activeList[8],
            "status10": activeList[9],
            "status11": activeList[10],
            "status12": activeList[11],
            "status13": activeList[12],
            "status14": activeList[13],
            "status15": activeList[14],
            "status16": activeList[15],
            "status17": activeList[16],
            "status18": activeList[17],
            "status19": activeList[18],
            "status20": activeList[19],
            "status21": activeList[20],
            "status22": activeList[21],
            "status23": activeList[22],
            "status24": activeList[23],
            "status25": activeList[24],
            "status26": activeList[25],
            "status27": activeList[26],
            "status28": activeList[27],
            "status29": activeList[28],
            "outp": puckposition,
        },
    )
