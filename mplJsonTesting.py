# Change Line 132 based on python version (2.7 or 3.6)
from common.bankList import *
from common.pckg import *
from common.smartOpsAuth import *
from datetime import datetime, timedelta
import threading
import csv
from requests.auth import HTTPBasicAuth

def callThreads(tList):
    #starts each thread
    for i in tList:
        i.start()
    #joins each thread
    for i in tList:
        i.join()

def mplDownload(id,url,link):
    global logData
    threadData=[]
    response=download_delta(id,url+link)
    for _i in response:
        for i in _i:
            for j in i:
                if (i[j] == None):
                    i[j] = ""
            timestamp = int((i["LogStart"])[6:-2])
            date = datetime.utcfromtimestamp(timestamp / 1000).strftime('%b %d %Y %H:%M:%S')

            threadData.append(
                [timestamp,id, str(i["Status"]), str(i["IntegrationFlowName"]), str(i["MessageGuid"]), date,
                 str(i["CorrelationId"]), \
                 str(i["Sender"]), str(i["Receiver"]), i["ApplicationMessageType"], i["ApplicationMessageId"]])
    logData.extend(threadData)

def logDownload(id, guid, cid, ):
    global eLog
    path = ".hana.ondemand.com/api/v1/MessageProcessingLogErrorInformations('"
    e = requests.get(Tenants[id][0] + path + guid + "')/$value", headers=hder)
    eLog.update({cid:e.text})  # Appended Error Text

def pushJson(data):
    print("*"*20+"Json Data"+"*"*20)
    print(data)  # Display the Json Data on the Console
    url = "https://api-smartops-dev.cfapps.sap.hana.ondemand.com/ibso/cpi"
    response = requests.post(url,data=json.dumps(data), headers=sOHder)
    print("Response Code: ", response.status_code)
    print("Response Text: ",response.text)  # Print the response text
    print("Response Headers: ",response.headers)  # print response headers

def format_data(data):
    jsonData=[]
    global eLog
    data = sorted(data, key=lambda x: x[6], )  # Sorting by Correlation id
    data.append(["x","x","x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"])
    unique_data = []
    unique_c_id = "Initial"
    unique_m_id = "Initial"
    unique_time = ""
    logThreadList=[]
    for i in data:
        if (i[6] != unique_c_id):
            #extract the last unique entry to make the API call for the error log.
            if (unique_c_id != "Initial"):
                logThreadList.append(threading.Thread(target=logDownload,args=(unique_data[-1][1],unique_m_id,unique_c_id)))

            unique_data.append(i)
            unique_c_id = i[6]
            unique_m_id = i[4]
            unique_time = i[0]

        else:
            if (i[0] < unique_time):  # we got the latest failure
                unique_data[-1][3] = unique_data[-1][3] + "<--" + i[3]  # Append Iflow_Name
                unique_data[-1][4] = unique_data[-1][4] + "|" + i[4]  # Append Message Id
                unique_data[-1][7] = i[7]
                unique_data[-1][8] = i[8]

            else:
                unique_data[-1][0] = i[0]
                unique_data[-1][1] = i[1]
                unique_data[-1][2] = i[2]
                unique_data[-1][3] = i[3] + "<--" + unique_data[-1][3]  # Append Iflow_Name
                unique_data[-1][4] = i[4] + "|" + unique_data[-1][4]  # Append Message Id
                unique_m_id = i[4]

            if (unique_data[-1][7] == "" and not i[7].startswith("Sender")):
                unique_data[-1][7] = i[7]

            if (unique_data[-1][8] == ""and not i[8].startswith("Receiver")):
                unique_data[-1][8] = i[8]

            if (unique_data[-1][9] == ""):
                if (i[8] != ""):
                    unique_data[-1][9] = i[9]  # Append AMType if unique

            if (unique_data[-1][9] == ""):
                if (i[9] != ""):
                    unique_data[-1][9] = i[9]  # Append AMID if unique

    #starting the threads to download the error log
    callThreads(logThreadList)

    #Creating final usable data with unique entries and error code defined
    del unique_data[-1]
    unique_data=list(x[1:] for x in unique_data)

    for i in unique_data:
        i.extend(["",i[0],"IBSO_DNT","00006","FSN"])
        if (i[5] in eLog):
            print(i[5],"-->",end= " ")
            print(eLog[i[5]])
            i.append(eLog[i[5]])
    header = ["Tenant", "Status", "IntegrationFlowName", "MessageGuid", "TimeStamp", "CorrelationId",
              "Sender", "Receiver", "ApplicationMessageType", "ApplicationId", "ErrorCode", "Client", "CheckGroup",
              "CheckID", "SystemRole", "ErrorInformation", ]

    for i in unique_data:
        tup=zip(header,i)
        dic={}
        for i,j in tup:
            dic[i]=j
        jsonData.append(dic)

    pushJson(jsonData)



read_time = datetime.utcnow()
end = read_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

try:
    with open('last_run.txt', "r") as f:
        start = f.read()
except:
    print("No Existing file exits so extracting log of last 60 min")
    start = (read_time - timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
eLog = {}
mplThreadList = []
logData = []
mplLink = ".hana.ondemand.com/api/v1/MessageProcessingLogs/?$inlinecount=allpages&$filter=(Status eq 'FAILED' or Status eq 'ESCALATED')\
     and LogEnd gt datetime'" + str(start) + "' and LogEnd lt datetime'" + str(end) + "'"

print("Download Started for time range --- ", start, " and ", end)
#Creating a thread for each of the tenants
for id, value in Tenants.items():
    mplThreadList.append(threading.Thread(target=mplDownload,args=(id,value[0],mplLink)))
callThreads(mplThreadList)

print("Download delta Function for all threads complete")
format_data(logData)

# start time for next run( .1 Second Overlap)
print("Updating timing for next run")
wr = (read_time - timedelta(seconds=0.1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
with open('last_run.txt', "w+") as f:
    f.write(wr)
