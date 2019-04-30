from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
import json
import requests



# Create your views here.


def load_isara(request):
    url='https://webjive.maxiv.lu.se/biomax/db'

    q = {'query': '{\n  device(name: "b311a-e/ctl/cats-01") {\n    attributes(pattern:"CassettePresence") {\n        name\n      value\n}\n    }\n  }\n  '}


    out=requests.post(url, data=json.dumps(q)).json()

    active=out["data"]["device"]["attributes"][0]["value"]
    #activeList=[str(x) for x in active]
    activeList=list()
    for i in active:
        if i==0:
            activeList.append("#82be00")
        else:
            activeList.append("#fea901")
    return render(request, 'laser/isara.html', {
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
        "status29":activeList[28]            
    })