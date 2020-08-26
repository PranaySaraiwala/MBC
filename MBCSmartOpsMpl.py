# Change Line 132 based on python version (2.7 or 3.6)
from common.bankList import *
from common.pckg import *
from common.smartOpsAuth import *
from datetime import datetime, timedelta
import threading

def startThreads(tList):
    #starts each thread
    for i in tList:
        i.start()

def joinThreads(tList):
    #joins each thread
    for i in tList:
        i.join()

def mplDownload(id,url,link):
    global errorCount
    global logData
    threadData=[]
    response,status=download_delta(id,url+link)
    errorCount.update({id: status})
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

@retry(tries=6,backoff=2)
def logDownload(id,value):
    global eLog

    path = ".hana.ondemand.com/api/v1/MessageProcessingLogErrorInformations('"
    e = requests.get(Tenants[id][0] + path + value[0] + "')/$value", headers=hder)
    eLog.update({value[1]:e.text})  # Appended Error Text
    print(value[1], "-->",e.text)


def QueueDownload(id, value ):
    count=0
    total=len(value)
    print("Failures in tenant: "+id+" = "+str(total))
    logThreadList=[]
    while total !=0:
        count += 1
        for i in range(0,10):

            if(total>0):
                #print(str(id)+" thread no= "+str(count)+str(i))
                t=threading.Thread(target=logDownload,args=(id,value.pop()))
                t.start()
                logThreadList.append(t)
                total = len(value)

        joinThreads(logThreadList)




    # for i in value:
    #     errorcode=""
    #     path = ".hana.ondemand.com/api/v1/MessageProcessingLogErrorInformations('"
    #     e = requests.get(Tenants[id][0] + path + i[0] + "')/$value", headers=hder)
    #     eLog.update({i[1]:[e.text]})  # Appended Error Text
    #     print(i[1], "-->",e.text)
    #     x = e.text
    #     matchfound = "Null"
    #     for ss in range(2, ignore_row_max + 1):
    #         if ((eval(str(ignore_sheet[str('A' + str(ss))].value))) == True):
    #             errorcode = ignore_sheet[str('B' + str(ss))].value
    #             matchfound = "Valid"
    #             break
    #     if (matchfound == "Null"):
    #         errorcode = "Unclassified"
    #         # append Errorcode to the the Row value
    #     eLog[i[1]].append(errorcode)

def pushJson(data):
    file_ext = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S-B')
    print("*"*20+"Json Data"+"*"*20)
    print(json.dumps(data))  # Display the Json Data on the Console
    lenData=len(data)
    print(lenData)
    for i in range(0,lenData,100):
        with open("MBCMpl_"+file_ext+str(i)+".json", "w") as f:

            batchData=data[i:i+100]
            print("Batch:", i)
            #print(json.dumps(batchData))
            json.dump(batchData, f, indent=4)

            url = "https://api-smartops-dev.cfapps.sap.hana.ondemand.com/ibso/cpi"
            response = requests.post(url,json=batchData, headers=sOHder)
            print("Response Code: ", response.status_code)
        # print("Response Text: ",response.text)  # Print the response text
        # print("Response Headers: ",response.headers)  # print response headers


def format_data(data):
    logQueue={}
    writeData=[]
    readData=[]
    jsonData=[]
    global eLog
    data = sorted(data, key=lambda x: x[6], )  # Sorting by Correlation id
    data.append(["x","x","x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x", "x"])
    unique_data = []
    unique_c_id = "Initial"
    unique_m_id = "Initial"
    unique_time = ""
    queueThreadList=[]
    for i in data:
        if (i[6] != unique_c_id):
            #extract the last unique entry to make the API call for the error log.
            if (unique_c_id != "Initial"):
                #logThreadList.append(threading.Thread(target=logDownload,args=(unique_data[-1][1],unique_m_id,unique_c_id)))

                #starts here
                if logQueue.get(unique_data[-1][1]) == None:
                    logQueue.update({str(unique_data[-1][1]) : []})
                logQueue[str(unique_data[-1][1])].append([unique_m_id,unique_c_id])



                #ends here

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



    #Creating final usable data with unique entries and error code defined
    del unique_data[-1]
    unique_data=list(x[1:] for x in unique_data)

    for key,value in logQueue.items():
        queueThreadList.append(threading.Thread(target=QueueDownload, args=(key, value)))

    startThreads(queueThreadList)
    joinThreads(queueThreadList)

    for i in unique_data:
        #i.extend(["",i[0],"IBSO_DNT","00006","FSN"])
        i.extend(["", "j0001", "IBSO_DNT", "00006", "FSN"])
        if (i[5] in eLog):
            i.append(eLog[i[5]])

    header = ["Tenant", "Status", "IntegrationFlowName", "MessageGuid", "TimeStamp", "CorrelationId",
              "Sender", "Receiver", "ApplicationMessageType", "ApplicationId", "ErrorCode", "Client", "CheckGroup",
              "CheckID", "SystemRole", "ErrorInformation", ]

    try:
        with open("prevCorr.txt","r") as f:
            readData=[x[:-1] for x in f.readlines()]
    except:
        readData=[]

    for i in unique_data:
        if i[5] not in readData:
            writeData.append(i[5])
            tup=zip(header,i)
            dic={}
            for i,j in tup:
                dic[i]=j
            jsonData.append(dic)

    with open("prevCorr.txt","w") as f:
        for i in writeData:
            f.write(i+"\n")

    pushJson(jsonData)

read_time = datetime.utcnow()
end = read_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

try:
    with open('last_run.txt', "r") as f:
        start = f.read()
except:
    print("No Existing file exits so extracting log of last 60 min")
    start = (read_time - timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
errorCount={}
eLog = {}
mplThreadList = []
logData = []
mplLink = ".hana.ondemand.com/api/v1/MessageProcessingLogs/?$inlinecount=allpages&$filter=(Status eq 'FAILED' or Status eq 'ESCALATED')\
     and LogEnd gt datetime'" + str(start) + "' and LogEnd lt datetime'" + str(end) + "'"

print("Download Started for time range --- ", start, " and ", end)
#Creating a thread for each of the tenants
for id, value in Tenants.items():
    mplThreadList.append(threading.Thread(target=mplDownload,args=(id,value[0],mplLink)))
startThreads(mplThreadList)
joinThreads(mplThreadList)

for i in Tenants.keys():
    if (errorCount.get(i)==None):
        print("Could not fetch log from: ",i)
        raise LookupError

print("Download delta Function for all threads complete")
#formatting the data into json
format_data(logData)

# start time for next run( .1 Second Overlap)
print("Updating timing for next run")
wr = (read_time - timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
with open('last_run.txt', "w+") as f:
    f.write(wr)
