# Change Line 132 based on python version (2.7 or 3.6)
from common.pckg import *
import threading
import csv
from requests.auth import HTTPBasicAuth
def read_JSON():
    with open('MBC_Logs.json', 'r') as myfile:
        data = json.load(myfile)

    print(data)  # Display the Json Data on the Console
    url = "https://api-smartops-dev.cfapps.sap.hana.ondemand.com/ibso/cpi"
    headers = {'Content-Type': 'application/json', "Accept": 'application/json'}
    response = requests.post(url, auth=HTTPBasicAuth(username='IBSO_SMARTOPS_USER', password='buk95gR7gb7%u1x'),
                             data=json.dumps(data), headers=headers)
    print("Response Code", response.status_code)

    print(response.text)  # Print the response text
    #
    # print(response.headers)  # print response headers
    # return (response.status_code)
    # print("After sending the Data")
    # print(data)


read_JSON()

