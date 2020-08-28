from common.smartOpsAuth import *
import requests
import json
def pushJson():

    # global end
    # batchData=[]
    # print("*"*20+"Json Data"+"*"*20)
    # print(json.dumps(data))  # Display the Json Data on the Console
    # lenData=len(data)
    # for i in range(0,lenData,100):
    #     with open("ICHLogs_"+end+"--"+str(i)+".json", "w") as f:
    #
    #         batchData=data[i:i+100]
    #         print("Batch:",i)
    #         print(json.dumps(batchData))
    #         json.dump(batchData, f, indent=4)

    response = requests.post(url,json=x, headers=sOHder)
    print("Response Code: ", response.status_code)
    print(x)
    print("Response Text: ",response.text)  # Print the response text
    print("Response Headers: ",response.headers)  # print response headers


print(__name__)