import requests
import json
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from laser.views.auth import proxies


def get_staff_all_proposals(url, token):
    r = requests.get(f"{url}/{token}/proposal/list")
    pList = json.loads(r.text)
    proposal_list = [pDict["Proposal_proposalNumber"] for pDict in pList]

    return sorted(proposal_list)


def get_proposals(username, password):
    proposals = list()
    # Connection and user parameters
    url_ispyb = "https://ispyb.maxiv.lu.se/ispyb/ispyb-ws/ispybWS/CrimsWebService?wsdl"

    # Authentication
    HTTPSoapService = HttpAuthenticated(username=username, password=password, proxy=proxies)
    client = Client(url_ispyb, transport=HTTPSoapService, cache=None, timeout=15)

    # Store shipping
    proteins = client.service.findProteinAcronyms()
    proposals = list(json.loads(proteins).keys())
    return proposals
