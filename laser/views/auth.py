import requests
import json

url = "https://ispyb.maxiv.lu.se/ispyb/ispyb-ws/rest"
site = "MAXIV"
proxies = {
    "http": "http://control.maxiv.lu.se:8888",
    "https": "http://control.maxiv.lu.se:8888",
    "no_proxy": "127.0.0.1,localhost,b-v-biomax-web-0,172.16.117.12,172.16.118.44,172.16.119.9,172.16.119.11,b-v-biomax-cc-0,172.16.118.48,b-biomax-eiger-dc-1,b311a-e-ctl-aem-01,b311a-e-ctl-aem-02,b311a-e-ctl-aem-03,172.16.119.15,b-v-biomax-web-1,172.16.116.23",
}


def authenticate(url, user, password, site, proxies):
    # return ISPyB auth token

    r = requests.post(
        url + "/authenticate?site=" + site,
        headers={"content-type": "application/x-www-form-urlencoded"},
        proxies=proxies,
        data={"login": user, "password": password},
        verify=True,
    )
    if "token" in r.text:
        token = json.loads(r.text)["token"]
        return token
    else:
        return False


def check_token(token):

    propsUrl = f"{url}/{token}/proposal/list"
    r = requests.get(propsUrl)
    if r.status_code == 403:
        os.system("rm static/.auth/session_auth.txt")
        os.system("rm static/.auth/session_user.txt")
