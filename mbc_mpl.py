# Change Line 132 based on python version (2.7 or 3.6)
from common.Bank_List import *
from common.pckg import *
from datetime import datetime, timedelta
import threading
import csv

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
    e = requests.get(eu2Tenants[id][0] + path + guid + "')/$value", headers=hder)
    eLog.update({cid:e.text})  # Appended Error Text
    print(cid)

def read_CSV(file, json_file):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        field = reader.fieldnames
        for row in reader:
            csv_rows.extend([{field[i]: row[field[i]] for i in range(len(field))}])
        with open(json_file, "w") as f:
            json_data = f.write(json.dumps(csv_rows, sort_keys=False, indent=4, separators=(',', ': ')))
            print(json_data)
            return json_data
            # read_JSON(file, json_file)

def read_JSON(json_file):
    with open(json_file, 'r') as myfile:
        data = json.load(myfile)

    print(data)  # Display the Json Data on the Console
    url = "https://api-smartops-dev.cfapps.us10.hana.ondemand.com/ibso/cpi"
    headers = {'Content-Type': 'application/json', "Accept": 'application/json'}
    response = requests.post(url, auth=HTTPBasicAuth(username='IBSO_SMARTOPS_USER', password='buk95gR7gb7%u1x'),
                             data=json.dumps(data), headers=headers)
    print(response.status_code)  # Print the Response Code
    print(response.text)  # Print the response text

    # print(response.headers)  # print response headers
    # return (response.status_code)
    print("After sending the Data")
    print(data)

def format_data(data):

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
                # path = ".hana.ondemand.com/api/v1/MessageProcessingLogErrorInformations('"
                # e = requests.get(eu2Tenants[unique_data[-1][1]][0] + path + unique_m_id + "')/$value", headers=hder)
                # unique_data[-1].append(e.text)  # Appended Error Text
                # print(i[6])

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
        if (eLog.get(i[5])==True):
            i.append(eLog[i[5]])

    with open('MBC_Logs.csv',"w") as csv_file:
        d_writer = csv.writer(csv_file)
        header = ["Client", "Status", "IntegrationFlowName", "MessageGuid", "TimeStamp", "CorrelationId",
                  "Sender", "Receiver", "ApplicationMessageType", "Application-Id", "ErrorInformation"]
        d_writer.writerow(header)
        # d_writer.writerows(data)
        d_writer.writerows(unique_data)

        read_CSV(file, json_file)

        read_JSON(json_file)

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
for id, value in eu2Tenants.items():
    mplThreadList.append(threading.Thread(target=mplDownload,args=(id,value[0],mplLink)))
callThreads(mplThreadList)

print("Download delta Function for all threads complete")
format_data(logData)

# start time for next run( .1 Second Overlap)
print("Updating timing for next run")
wr = (read_time - timedelta(seconds=0.1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
with open('last_run.txt', "w+") as f:
    f.write(wr)
