
from common.fetchMpl import *


#*******------PRE CHECK--------**********

#Check the SmartOps endpoint and the checkGroup Ids for dev/prod
#for ICH check the error category

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

def updateTime(read_time):
    # start time for next run( 3 Second Overlap)
    print("Updating timing for next run")
    wr = (read_time - timedelta(seconds=3)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    with open('last_run.txt', "w+") as f:
        f.write(wr)

def main():


    start, end,read_time = timeRange()
    mplLink = ".hana.ondemand.com/api/v1/MessageProcessingLogs/?$inlinecount=allpages&$filter=(Status eq 'FAILED' or Status eq 'ESCALATED')\
     and LogEnd gt datetime'" + str(start) + "' and LogEnd lt datetime'" + str(end) + "'"


    logData,errorCount=startFetch(Tenants,mplLink)

    checkError(Tenants,errorCount)

    #formatting the data into json
    format_data(logData)

    updateTime(read_time)

main()


