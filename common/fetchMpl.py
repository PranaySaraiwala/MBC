from common.pckg import *
from common.smartOpsAuth import *
from common.mbcFetchConfig import *
from datetime import datetime, timedelta
import threading


def timeRange():
    read_time = datetime.utcnow()
    end = read_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    try:
        with open('last_run.txt', "r") as f:
            start = f.read()
    except:
        print("No Existing file exits so extracting log of last 60 min")
        start = (read_time - timedelta(minutes=60)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

    print("Download Started for time range --- ", start, " and ", end)

    return start,end,read_time

def startFetch(tenant,mplLink):
    errorCount={}
    logData=[]
    mplThreadList = []

    for id, value in tenant.items():
        mplThreadList.append(threading.Thread(target=mplDownload,args=(id,value[0],mplLink,logData,errorCount)))

    startThreads(mplThreadList)
    joinThreads(mplThreadList)

    return logData,errorCount

def checkError(tenant,errorCount):
    for i in tenant.keys():
        if (errorCount.get(i)==None):
            print("Could not fetch log from: ",i)
            raise LookupError

def pushErrorCheck(data):

    if(len(data)!=0):
        for key,value in data.items():
            print("Affected batch: ",key)
            print("Error: ",value)

        raise Exception("Not all push were successful")

def updateTime(read_time):
    # start time for next run( 3 Second Overlap)
    print("Updating timing for next run")
    wr = (read_time - timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    with open('last_run.txt', "w+") as f:
        f.write(wr)

def addAdditionalData(eLog,data,Client,CheckGroup,CheckID,SystemRole):
    for i in data:
        if(Client!=""):
            i.extend([Client,CheckGroup,CheckID,SystemRole])
        else:
            i.extend([i[0], CheckGroup, CheckID, SystemRole])

        if (i[5] in eLog):
            i.extend(eLog[i[5]])
    return data

def startThreads(tList):
    #starts each thread
    for i in tList:
        i.start()

def joinThreads(tList):
    #joins each thread
    for i in tList:
        i.join()

def mplDownload(id,url,link,logData,errorCount):
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

def QueueDownload(id, value,eLog):
    count=0
    total=len(value)
    print("Failures in tenant: "+id+" = "+str(total))
    logThreadList=[]
    while total !=0:
        count += 1
        for i in range(0,10):

            if(total>0):
                #print(str(id)+" thread no= "+str(count)+str(i))
                t=threading.Thread(target=logDownload,args=(id,value.pop(),eLog))
                t.start()
                logThreadList.append(t)
                total = len(value)

        joinThreads(logThreadList)

@retry(tries=3,backoff=2)
def pushJson(data,num,file,url):
    print("url=",url)
    file_ext = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S-B')
    print("Pushing Batch:", num)
    print(json.dumps(data))

    try:
        response = requests.post(url, json=data, headers=sOHder)
        statusCode=response.status_code
        print("Response Code: ", response.status_code)

        if(statusCode !=200):
            return statusCode
        else:
            for i in data:
                file.write(i["CorrelationId"] + "\n")

            with open("Mpl_" + file_ext + str(num) + ".json", "w") as f:
                json.dump(data, f, indent=4)
            return "Ok"


    except Exception as e:
        print(e)
        raise Exception("Push Operation for Batch {} failed".format(num))

def splitJson(data,url,splitCount=80):
    status={}

    print("*"*20+"Json Data"+"*"*20)
    #print(json.dumps(data))  # Display the Json Data on the Console
    lenData=len(data)
    print("total count= ",lenData)
    with open("prevCorr.txt", "w") as file:
        for i in range(0,lenData,splitCount):
            batchData=data[i:i+splitCount]
            retValue=pushJson(batchData,i,file,url)
            if(retValue != "Ok"):
                status.update({i:retValue})
    return status

def returnCheckData():
    try:
        with open("prevCorr.txt","r") as f:
            readData=[x[:-1] for x in f.readlines()]
    except:
        readData=[]

    return readData

def createJson(data,checkData):
    count=0
    jsonData=[]
    header = ["Tenant", "Status", "IntegrationFlowName", "MessageGuid", "TimeStamp", "CorrelationId",
              "Sender", "Receiver", "ApplicationMessageType", "ApplicationId", "Client", "CheckGroup",
              "CheckID", "SystemRole", "ErrorInformation", "ErrorCode"]

    for i in data:
        if i[5] not in checkData:
            tup=zip(header,i)
            dic={}
            for i,j in tup:
                dic[i]=j
            jsonData.append(dic)
        else:
            count+=1


    print("Total Duplicates from previous run :",count)
    return jsonData

def format_data(data,url,extendData):
    checkData=returnCheckData()
    logQueue={}
    eLog={}
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
                if logQueue.get(unique_data[-1][1]) == None:
                    logQueue.update({str(unique_data[-1][1]) : []})
                logQueue[str(unique_data[-1][1])].append([unique_m_id,unique_c_id])

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

    #Creating final usable data with unique entries and error code defined
    del unique_data[-1]
    unique_data=list(x[1:] for x in unique_data)

    for key,value in logQueue.items():
        queueThreadList.append(threading.Thread(target=QueueDownload, args=(key, value,eLog)))

    startThreads(queueThreadList)
    joinThreads(queueThreadList)

    unique_data=addAdditionalData(eLog,unique_data,*extendData)

    jsonData=createJson(unique_data,checkData)

    pushStatus=splitJson(jsonData,url)
    return pushStatus

