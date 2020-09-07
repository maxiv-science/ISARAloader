from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django import forms
import json
import requests
import os
from glob import glob
from suds.client import Client
from suds.transport.http import HttpAuthenticated
import serial
import subprocess
import time

ser = serial.Serial()
#ser.port = '/dev/cu.usbmodem14513101'
ser.port = '/dev/ttyACM0'
ser.baudrate = 9600
ser.timeout = 1
# open port if not already open
if ser.isOpen() == False:
    ser.open()



token=""
url="https://ispyb.maxiv.lu.se/ispyb/ispyb-ws/rest"
site="MAXIV"
proxies = {
      'http': "http://control.maxiv.lu.se:8888",
      'https': "http://control.maxiv.lu.se:8888",
      'no_proxy': "127.0.0.1,localhost,b-v-biomax-web-0,172.16.117.12,172.16.118.44,172.16.119.9,172.16.119.11,b-v-biomax-cc-0,172.16.118.48,b-biomax-eiger-dc-1,b311a-e-ctl-aem-01,b311a-e-ctl-aem-02,b311a-e-ctl-aem-03,172.16.119.15,b-v-biomax-web-1,172.16.116.23",
       }

staff_list=["biomax-user","ishgor","gorgisyan","guslim","anagon","mirmil","uwemul","jienan","vlatal","johung","thours","oskaur","monbje"]

def get_staff_all_proposals(url, token):
    r=requests.get(f"{url}/{token}/proposal/list")
    pList=json.loads(r.text)
    proposal_list=[pDict["Proposal_proposalNumber"] for pDict in pList]

    return sorted(proposal_list)


def check_token(token):
    URL="https://ispyb.maxiv.lu.se/ispyb/ispyb-ws/rest"
    propsUrl = f"{URL}/{token}/proposal/list"
    r = requests.get(propsUrl)
    if r.status_code == 403:
        os.system("rm static/.auth/session_auth.txt")
        os.system("rm static/.auth/session_user.txt")

def get_proposals(username,password):
    proposals=list()
    # Connection and user parameters
    url_ispyb = "https://ispyb.maxiv.lu.se/ispyb/ispyb-ws/ispybWS/CrimsWebService?wsdl" 

    # Authentication 
    HTTPSoapService = HttpAuthenticated(username = username, password = password, proxy=proxies ) 
    client = Client( url_ispyb, transport = HTTPSoapService, cache = None, timeout = 15 )

    # Store shipping
    proteins = client.service.findProteinAcronyms()
    proposals=list(json.loads(proteins).keys())
    return proposals

def authenticate(url, user, password, site, proxies):
    #return ISPyB auth token

    r = requests.post(url + '/authenticate?site=' + site, headers={'content-type': 'application/x-www-form-urlencoded'}, proxies=proxies, data={'login': user, 'password': password}, verify=True)
    if "token" in r.text:
        token = json.loads(r.text)['token']
        return token
    else:
        return False

def update_puck_location_ISARA(url,token,proposal,containerId,ISARA_position):
    #To update the sample changer location using the REST api post request
    # -Proposal: MX + proposal number. Ex: MX20180479
    # -authentication token
    # -containerId: unique numerical id from the puck. Ex:1256
    # -sample location:
    containerId=str(containerId)
    requests.post(url+"/"+token+"/proposal/MX"+proposal+"/container/"+containerId+"/beamline/BioMAX/samplechangerlocation/update", data={"sampleChangerLocation": ISARA_position}, verify=True)
    
def update_dewar_status(url,token,proposal,shippingId,status):
    #update dewar status
    # -ShippingID: 207

    ## Examples:
    #shippingId="207"
    #status="at_MAXIV"
    #status="processing"
    #status="OPENED"
    shippingId=str(shippingId)
    requests.get(url+"/"+token+"/proposal/MX"+proposal+"/shipping/"+shippingId+"/status/"+status+"/update")

    print("ShippingId "+shippingId+" updated to "+status)
    if status=="processing":
        print("You can now load pucks into ISARA")

def get_shipping_names_and_Ids(dumps):
    #list of shipping names and Ids for a given user proposal
    name_ID={x["shippingName"]:x["shippingId"] for x in dumps}
    return name_ID

def get_pucks_in_dewar(dumps,shippingId):
    pucks_in_shipment=dict()
    for dump in dumps:
        if dump["shippingId"]==shippingId:
            pucks_in_shipment[dump["containerCode"]]=dump["containerId"]

    return pucks_in_shipment

def get_dewar_status(dumps,shippingName):
    #give the current shipping status
    try:
        for dump in dumps:
            if dump["shippingName"]==shippingName:
                shippingStatus=dump["shippingStatus"]
                break
    except:
        shippingStatus="unknown"
    return shippingStatus

def unload_all_shipments(token,proposal,dumps):
    #remove all shipments from sessions
    #all shipments will be set from "processing" to "at_MAXIV"
    #other status will be kept untouched
    processing_Ids=dict()
    for dump in dumps:
        if dump["shippingStatus"]=="processing":
            processing_Ids[dump["shippingId"]]=dump["shippingStatus"]

    for shippingId in processing_Ids:
        status="at_MAXIV"
        update_dewar_status(url,token,proposal,shippingId,status)

def unload_all_pucks(token,proposal,dumps):
    #get list of pucks loaded in ISARA from "processing" shipments
    #unload all pucks
    #Pucks in dewars that are marked as anything but processing will remain untouched

    puckList=list()
    for dump in dumps:
        if dump["shippingStatus"]=="processing":
            if dump["sampleChangerLocation"]!="":
                puckList.append(dump["containerId"])

    for puck in puckList:
        update_puck_location_ISARA(url,token,proposal,puck,"")
    print("All pucks were unloaded for proposal: "+proposal)
    print(time.ctime())
    unload_all_shipments(token,proposal,dumps)

def get_next_empty_placeholder(active,shipments,sampleChanger_position,dumps):

    if os.path.exists("static/unsafe_positions.txt"):
        with open("static/unsafe_positions.txt","r") as readFile:
            r=readFile.read()
        r=r.replace("checked","1")
        r=r.replace("false","0")
        disabled_position=r.split(",")
        disabled_position=list(map(int,disabled_position))

    else:
        disabled_position=[]
    #Creates dewar:status dictionary from available shipments
    inUse_position=list()
    dewars_status={x:get_dewar_status(dumps,x) for x in shipments.keys()}
    for key, value in dewars_status.items():
        if value=="processing":
            for k,v in shipments[key].items():
                if type(sampleChanger_position[k]) is str and sampleChanger_position[k]!="Dry shipper":
                    inUse_position.append(sampleChanger_position[k]) 
    
    inUse_position=list(filter(lambda a: a != '', inUse_position))
    inUse_position=list(map(int,inUse_position))
    
    #print(disabled_position)
    for n,i in enumerate(active):
        if i==1:
            inUse_position.append(n+1)    
    #inUse_position=inUse_position+disabled_position
    #dewar_pos=list(range(1,30))
    #n_empty=list(set(dewar_pos)-set(inUse_position))[0]

    # List of positions assigned in the current session
    # If the puck was assigned but not place in the sample changer, this will avoid 
    # double assigning 
    session_assingned=[dump["sampleChangerLocation"] for dump in dumps if dump["containerStatus"]=="processing"]
    session_assingned=[int(x) for x in session_assingned if x!="" and x is not None]

    isara_sc=dict()
    for n,i in enumerate(active,1):
        if i==0:
            isara_sc[n]="free"
        else:
            isara_sc[n]="in_use"
    for n,i in enumerate(disabled_position,1):
        if i==0:
            isara_sc[n]="in_use"
    for i in inUse_position:
        isara_sc[i]="in_use"
    for i in session_assingned:
        isara_sc[i]="in_use"
    for pos, status in isara_sc.items():
        if status=="free":
            n_empty=pos
            break


    print("isara_sc:",isara_sc)
    print("n_empty: ",n_empty)    
    print(time.ctime())
    return n_empty

def duo_login(request):
    message="Please login with your DUO account"
    proposals=None
    login_state="0"
    if os.path.exists("static/.auth/session_auth.txt"):
        login_state="1"
        if os.path.exists("static/.auth/session_user.txt"):
            with open("static/.auth/session_user.txt") as r:
                fcontent=r.read()
            user,proposals=fcontent.split(";")
            proposals=proposals.split(",")
            with open("static/.auth/session_auth.txt","r") as readFile:
                token=readFile.read()
                token=token.split(",")[0]

            if user in staff_list:
                proposals=get_staff_all_proposals(url, token)
            print("user, proposals"+str(fcontent))
            print(time.ctime())
        return render(request, "laser/duo_login.html",{
            "login":user,
            "proposals":proposals,
            "login_state":login_state,
            "message":""
            })
    elif request.POST.get("login") and request.POST.get("password"):
        login=request.POST.get("login")
        password=request.POST.get("password")
        session_token=authenticate(url,login,password,site,proxies)
        

        if not session_token:  
            #checks if token exists based on login and password, 
            #if not, refuses connection and ask user to try again          
            login_state="0"
            return render(request, "laser/duo_login.html", {
                "login_state":login_state,                
                "login":login,
                "password":password,
                "message":"Wrong username and/or password"
                })
        else:            
            #if authentication works
            #change login state to 0
            #get list of proposals
            proposals=get_proposals(login,password)            
            login_state="1"
            token=authenticate(url,login,password,site,proxies)
            if login in staff_list:
                proposals=get_staff_all_proposals(url, token)
            #create session files with user, proposals and token
            os.makedirs("static/.auth",exist_ok=True)
            with open("static/.auth/session_auth.txt","w") as writeFile:
                writeFile.write(token+","+proposals[0])
            with open("static/.auth/session_user.txt","w") as writeFile:
                writeFile.write(login+";"+",".join(proposals))
            
            return render(request, "laser/duo_login.html", {
                "login_state":login_state,
                "proposals":proposals,
                "login":login,
                "password":password,
                "message":"Login OK"
                })
    else:
        #starts new session if no token file is available
        login_state="0"
        return render(request, "laser/duo_login.html",{
            "login_state":login_state,
            "message":message
            })

def duo_logout(request):

    login_state="0"
    message="You logged out"
    if os.path.exists("static/.auth/session_auth.txt"):
        os.system("rm static/.auth/session_auth.txt")
        os.system("rm static/.auth/session_user.txt")
        return render(request, "laser/duo_login.html/",{
                "login_state":login_state,
                "message":message
                })
    else:
        return render(request, "laser/duo_login.html/",{
                "login_state":login_state,
                "message":message
                })

def get_samples_in_puck(url, token, proposal, containerId):
    #reads the samples declared in a given puck Id (number code)
    #returns a list with puck name, code, and 16 definitions of filled-empty 
    #this can be parsed as classes inside html template
    r=requests.get(url+"/"+token+"/proposal/MX"+proposal+"/mx/sample/containerid/"+containerId+"/list")
    pucks_dict=json.loads(r.text)
    containerName=pucks_dict[0]["Container_code"]    
    empty_places=list(set(map(str,list(range(1,17))))-set([x["BLSample_location"] for x in pucks_dict]))
    l=["sample-filled"]*16
    for x in empty_places:
        l[int(x)-1]="sample-empty"

    print("containerId:", containerId)
    print("containerName:", containerName)
    print("l:", l)
    print(time.ctime())    
    return [containerId,containerName]+l


def safe_pucks(request):
    ISARA_pos=str(request.GET.get("savebtn"))
    pantilt=str(request.GET.get("movebtn"))
    if "None" not in ISARA_pos:
        with open("static/unsafe_positions.txt","w") as writeFile:
            ISARA_pos=ISARA_pos.replace("true","checked")
            writeFile.write(ISARA_pos)
    if "None" not in pantilt:
        pan,tilt=pantilt.split(",")
        pos=int(pan)
        data=bytes([10])+bytes([pos])
        data+=bytes([5])+bytes([pos])
        ser.write(data)

    if os.path.exists("static/unsafe_positions.txt"):
        with open("static/unsafe_positions.txt","r") as readfile:
            position_state=readfile.readlines()[0].split(",")
        
        state1=position_state[0]
        state2=position_state[1]
        state3=position_state[2]
        state4=position_state[3]
        state5=position_state[4]
        state6=position_state[5]
        state7=position_state[6]
        state8=position_state[7]
        state9=position_state[8]
        state10=position_state[9]
        state11=position_state[10]
        state12=position_state[11]
        state13=position_state[12]
        state14=position_state[13]
        state15=position_state[14]
        state16=position_state[15]
        state17=position_state[16]
        state18=position_state[17]
        state19=position_state[18]
        state20=position_state[19]
        state21=position_state[20]
        state22=position_state[21]
        state23=position_state[22]
        state24=position_state[23]
        state25=position_state[24]
        state26=position_state[25]
        state27=position_state[26]
        state28=position_state[27]
        state29=position_state[28]
    else:
        state1="checked"
        state2="checked"
        state3="checked"
        state4="checked"
        state5="checked"
        state6="checked"
        state7="checked"
        state8="checked"
        state9="checked"
        state10="checked"
        state11="checked"
        state12="checked"
        state13="checked"
        state14="checked"
        state15="checked"
        state16="checked"
        state17="checked"
        state18="checked"
        state19="checked"
        state20="checked"
        state21="checked"
        state22="checked"
        state23="checked"
        state24="checked"
        state25="checked"
        state26="checked"
        state27="checked"
        state28="checked"
        state29="checked"

    return render(request, "laser/safe_pucks.html", {
        "state1":state1,
        "state2":state2,
        "state3":state3,
        "state4":state4,
        "state5":state5,
        "state6":state6,
        "state7":state7,
        "state8":state8,
        "state9":state9,
        "state10":state10,
        "state11":state11,
        "state12":state12,
        "state13":state13,
        "state14":state14,
        "state15":state15,
        "state16":state16,
        "state17":state17,
        "state18":state18,
        "state19":state19,
        "state20":state20,
        "state21":state21,
        "state22":state22,
        "state23":state23,
        "state24":state24,
        "state25":state25,
        "state26":state26,
        "state27":state27,
        "state28":state28,
        "state29":state29,
    })
    
def load_isara(request):
    print("Moving laser in ISARA...")
    print(time.ctime())
    #check for unload all pucks options
    unloadCMD=str(request.GET.get("unloadbutton"))
    user=""
    if "unloadALL" in unloadCMD:
        if os.path.exists("static/.auth/session_auth.txt"):
            with open("static/.auth/session_auth.txt","r") as r:
                fcontent=r.read()
            token,proposal=fcontent.split(",")
            proposal=proposal.replace("MX","")
            response=requests.get(url+"/"+token+"/proposal/MX"+proposal+"/dewar/list")
            dumps=response.json()   
            unload_all_pucks(token,proposal,dumps)
    
    #Tango device for ISARA 
    #Read information about used positions on SC
    #Green is free, Orange is in use
    #returns a list "active" with 0s and 1s
    shipments=[""]
    pucks_in_shipment=[""]
    next_empty=""
    puck_mounted_dict={}
    url_jive='https://webjive.maxiv.lu.se/biomax/db'

    q = {'query': '{\n  device(name: "b311a-e/ctl/cats-01") {\n    attributes(pattern:"CassettePresence") {\n        name\n      value\n}\n    }\n  }\n  '}

    if request.method == 'POST':
        proposalID = request.POST.get("proposalID")    
        proposal=proposalID   
        os.makedirs("static/.auth",exist_ok=True)
        if proposalID and os.path.exists("static/.auth/session_auth.txt"):
            proposal=proposalID
            with open("static/.auth/session_auth.txt","r") as readFile:
                token=readFile.read()
                token=token.split(",")[0]
            with open("static/.auth/session_auth.txt","w") as writeFile:
                writeFile.write(token+","+proposal)
        with open("static/.auth/session_proposal.txt","w") as writeFile:
            writeFile.write(proposalID)



    if os.path.exists("static/.auth/session_auth.txt"):	
        with open("static/.auth/session_auth.txt","r") as r:
            fcontent=r.read()
        token,proposal=fcontent.split(",")
        with open("static/.auth/session_proposal.txt","r") as r:
            fcontent=r.read()        
        proposal=fcontent.split()[0]

        proposal=proposal.replace("MX","")
        check_token(token)
        if os.path.exists("static/.auth/session_user.txt"):
	        with open("static/.auth/session_user.txt") as r:
        	    fcontent=r.read()
	        user,proposals=fcontent.split(";")
        	proposals=proposals.split(",")
        else:
            proposal=""
            token=""
    else:
        proposal=""
        token=""

    
    puckposition="None"
    puckposition=str(request.GET.get("puckpos"))
    data=''
    print(puckposition)
    
    if "None" not in puckposition:
        puckposition=puckposition.replace("position","")
        pos=int(puckposition)
        data=bytes([10])+bytes([pos])
        data+=bytes([5])+bytes([pos])
        ser.write(data)
    out=requests.post(url_jive, data=json.dumps(q), verify = False).json()


    active=out["data"]["device"]["attributes"][0]["value"]
    
    activeList=list()
    for i in active:
        if i==0:
            activeList.append("unipuck-free")
        else:
            activeList.append("unipuck-occupied")

    print("Baskets in use..")
    print("activeList", activeList)
    #ISPyB listing from available shippings and pucks
    shippingName=str(request.GET.get("select_shipment"))
    containerId=str(request.GET.get("containerId"))
    print("shippingName and containerId")
    print(shippingName,containerId)
    if token!="":
        response=requests.get(url+"/"+token+"/proposal/MX"+proposal+"/dewar/list")
        dumps=response.json()
        #Creates dictionary of dewars (shippingName/Id)
        #with values = pucks inside the dewar (containerName/Id)    
        shipments=dict()
        shippingId_dict=dict()
        sampleChanger_position=dict()
        sampleChanger_positionId=dict()
        for dump in dumps:
            Id=dump["shippingId"]
            Name=dump["shippingName"]    
            pucks=get_pucks_in_dewar(dumps,int(Id))
            shipments[Name]=pucks
            #Create dictionary with pucks and their assignement inside SC (ISPyB)
            #Does not filter for processing only 
            sc_position=dump["sampleChangerLocation"]
            sampleChanger_position[dump["containerCode"]]=sc_position
            sampleChanger_positionId[dump["containerId"]]=sc_position
            for key,value in pucks.items():
                shippingId_dict[value]=Name
        
        print("shippingId_dict: ", shippingId_dict)
        
        if shippingName=="None":
            if containerId=="None":
                pucks_in_shipment=""
            else:
                shippingName=shippingId_dict[int(containerId)]
                pucks_in_shipment=shipments[shippingName]
                
                if get_dewar_status(dumps,shippingName)!="processing":
                    shippingId=get_shipping_names_and_Ids(dumps)[shippingName]
                    
                    update_dewar_status(url,token,proposal,shippingId,"processing")
                #print(containerId)                
                SC_position=sampleChanger_positionId[int(containerId)]
                #print(SC_position)
                if SC_position=="" or SC_position==None:
                    print("Searching next available position for the puck...")
                    print(containerId)
                    #print("HERE")
                    next_empty=get_next_empty_placeholder(active,shipments,sampleChanger_position,dumps)
                    update_puck_location_ISARA(url,token,proposal,containerId,next_empty)
                    print("Next available position is ")
                    print(next_empty)
                    pos=int(next_empty)
                    data=bytes([10])+bytes([pos])
                    data+=bytes([5])+bytes([pos])
                    ser.write(data)
                    #print(shippingName)
                    #print(next_empty)
                    puck_mounted_dict[containerId]=next_empty
                    print("puck_mounted_dict:", puck_mounted_dict)
                else:
                    pos=SC_position
                    try:
                        pos= int(pos)
                        data=bytes([10])+bytes([pos])
                        data+=bytes([5])+bytes([pos])
                        ser.write(data)
                    except:
                        pass
        else:
            pucks_in_shipment=shipments[shippingName]
            print("pucks_in_shipment:", pucks_in_shipment)
        
    try:
        del pucks_in_shipment[None]
    except:
        pass
    print("After puck_in_shipment cleanup")
    print(pucks_in_shipment)
    try:
        pucks_in_shipment=shipments[shippingName]
        for key, value in pucks_in_shipment.items():
            puck_mounted_dict[value]=sampleChanger_positionId[int(value)]
    except:
        pass
    
    samples_in_pucks_status=list()
    sample_avail="none"
    try:
        for i in pucks_in_shipment.values():
            st=get_samples_in_puck(url, token, proposal, str(i))
            samples_in_pucks_status.append(st)
            sample_avail="OK"
    except:
        samples_in_pucks_status=[[containerId,"Unipuck Example"]+["sample-empty"]*16]
        sample_avail="none"
    #print(pucks_in_shipment)

    #print(shipments)
    print(samples_in_pucks_status)
    if user in staff_list:
        userstate="staff"
    else:
        userstate="visitor"

    with open("static/unsafe_positions.txt","r") as readfile:
        position_state=readfile.readlines()[0].split(",")
    indices = [i for i, x in enumerate(position_state) if x == "false"]
    for index_i in indices:
        activeList[index_i]="unipuck-disabled"
    print(time.ctime())
    return render(request, 'laser/isara.html', {
        "userstate":user,
        "proposal":proposal,
        "shipments":shipments,
        "select_shipment":shippingName,
        "pucks_in_shipment":pucks_in_shipment,
        "puck_mounted_dict":puck_mounted_dict,
        "samples_in_pucks_status":samples_in_pucks_status,
        "containerId":containerId,
        "sample_avail":sample_avail,
        "next_empty":next_empty,
        "active":activeList,
        "status1":activeList[0],
        "status2":activeList[1 ],
        "status3":activeList[2 ],
        "status4":activeList[3 ],
        "status5":activeList[4 ],
        "status6":activeList[5 ],
        "status7":activeList[6 ],
        "status8":activeList[7 ],
        "status9":activeList[8 ],
        "status10":activeList[9 ],
        "status11":activeList[10],
        "status12":activeList[11],
        "status13":activeList[12],
        "status14":activeList[13],
        "status15":activeList[14],
        "status16":activeList[15],
        "status17":activeList[16],
        "status18":activeList[17],
        "status19":activeList[18],
        "status20":activeList[19],
        "status21":activeList[20],
        "status22":activeList[21],
        "status23":activeList[22],
        "status24":activeList[23],
        "status25":activeList[24],
        "status26":activeList[25],
        "status27":activeList[26],
        "status28":activeList[27],
        "status29":activeList[28],
        "outp":puckposition
    })

