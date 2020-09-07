import time
import requests
import json
from laser.views.auth import url


def update_puck_location_ISARA(url, token, proposal, containerId, ISARA_position):
    # To update the sample changer location using the REST api post request
    # -Proposal: MX + proposal number. Ex: MX20180479
    # -authentication token
    # -containerId: unique numerical id from the puck. Ex:1256
    # -sample location:
    containerId = str(containerId)
    requests.post(
        url
        + "/"
        + token
        + "/proposal/MX"
        + proposal
        + "/container/"
        + containerId
        + "/beamline/BioMAX/samplechangerlocation/update",
        data={"sampleChangerLocation": ISARA_position},
        verify=True,
    )


def update_dewar_status(url, token, proposal, shippingId, status):
    # update dewar status
    # -ShippingID: 207

    # Examples:
    # shippingId="207"
    # status="at_MAXIV"
    # status="processing"
    # status="OPENED"
    shippingId = str(shippingId)
    requests.get(
        url + "/" + token + "/proposal/MX" + proposal + "/shipping/" + shippingId + "/status/" + status + "/update"
    )

    print("ShippingId " + shippingId + " updated to " + status)
    if status == "processing":
        print("You can now load pucks into ISARA")


def get_shipping_names_and_Ids(dumps):
    # list of shipping names and Ids for a given user proposal
    name_ID = {x["shippingName"]: x["shippingId"] for x in dumps}
    return name_ID


def get_pucks_in_dewar(dumps, shippingId):
    pucks_in_shipment = dict()
    for dump in dumps:
        if dump["shippingId"] == shippingId:
            pucks_in_shipment[dump["containerCode"]] = dump["containerId"]

    return pucks_in_shipment


def get_dewar_status(dumps, shippingName):
    # give the current shipping status
    try:
        for dump in dumps:
            if dump["shippingName"] == shippingName:
                shippingStatus = dump["shippingStatus"]
                break
    except:  # noqa
        shippingStatus = "unknown"
    return shippingStatus


def unload_all_shipments(token, proposal, dumps):
    # remove all shipments from sessions
    # all shipments will be set from "processing" to "at_MAXIV"
    # other status will be kept untouched
    processing_Ids = dict()
    for dump in dumps:
        if dump["shippingStatus"] == "processing":
            processing_Ids[dump["shippingId"]] = dump["shippingStatus"]

    for shippingId in processing_Ids:
        status = "at_MAXIV"
        update_dewar_status(url, token, proposal, shippingId, status)


def unload_all_pucks(token, proposal, dumps):
    # get list of pucks loaded in ISARA from "processing" shipments
    # unload all pucks
    # Pucks in dewars that are marked as anything but processing will remain untouched

    puckList = list()
    for dump in dumps:
        if dump["shippingStatus"] == "processing":
            if dump["sampleChangerLocation"] != "":
                puckList.append(dump["containerId"])

    for puck in puckList:
        update_puck_location_ISARA(url, token, proposal, puck, "")
    print("All pucks were unloaded for proposal: " + proposal)
    print(time.ctime())
    unload_all_shipments(token, proposal, dumps)


def get_samples_in_puck(url, token, proposal, containerId):
    # reads the samples declared in a given puck Id (number code)
    # returns a list with puck name, code, and 16 definitions of filled-empty
    # this can be parsed as classes inside html template
    r = requests.get(url + "/" + token + "/proposal/MX" + proposal + "/mx/sample/containerid/" + containerId + "/list")
    pucks_dict = json.loads(r.text)
    containerName = pucks_dict[0]["Container_code"]
    empty_places = list(set(map(str, list(range(1, 17)))) - set([x["BLSample_location"] for x in pucks_dict]))
    l_filled = ["sample-filled"] * 16
    for x in empty_places:
        l_filled[int(x) - 1] = "sample-empty"

    print("containerId:", containerId)
    print("containerName:", containerName)
    print("l:", l_filled)
    print(time.ctime())
    return [containerId, containerName] + l_filled
