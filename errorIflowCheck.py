# coding=utf-8
import threading
from common.Auth import *
import json
import requests
from common.cluster import *


def prepareData(data,code):
    x = {}
    for i, j in data.items():
        if(code==201):
            if j['Status'] != "Ok":
                x.update({i:{}})
                x[i].update(j)
        else:
            x.update({i: {}})
            x[i].update(j)
    return x

def main(tenantList):
    flag = 0
    result = {}
    err = {}
    threadList = []

    #API Urls to call
    checkUrl = ".hana.ondemand.com/api/v1/IntegrationRuntimeArtifacts/?$inlinecount=allpages&$filter=Status eq 'ERROR' or Status eq 'FAILED'"

    def callThreads(tList):
        #starts each thread
        for i in tList:
            i.start()
        #joins each thread
        for i in tList:
            i.join()

    def connectionCheck(id,tenantUrl,name,checkUrl):
        nonlocal flag,result,err
        response=""
        home=".hana.ondemand.com/itspaces/shell/monitoring/Overview"

        try:
            print("Requesting Status from " +id)
            r = requests.get(tenantUrl + checkUrl, headers=hder)
            response = json.loads(r.text)
        except Exception as e:
            print(e)
            print("Cannot fetch result from " + id)
            err.update({id: [id, str(e), tenantUrl + home]})

        errorCount = int(response["d"]["__count"])

        if (errorCount == 0):
            result.update({id: {'Status':'Ok'}})
        else:
            flag = 1
            for data in response["d"]["results"]:
                sData = {'Id':data["Id"],'Version':data["Version"],'Name':data["Name"]}

                if (result.get(id) == None):
                    result.update({id: {'Status':'Error','Count':errorCount,'Name':name,'URL': tenantUrl + home,'IflowDetails':[]}})

                result[id]['IflowDetails'].append(sData)



    for id, value in tenantList.items():
        #Creating a thread for each of the tenants
        threadList.append(threading.Thread(target=connectionCheck,args=(id,value[0],value[1],checkUrl,)))

    callThreads(threadList)

    #execution resumes here once all threads have completed executing.

    print("All Threads Completed\n")
    print("*"*20+"RESULT"+"*"*20)

    if(flag==0 and len(err)==0):
        print("No Failed Iflows")
        print("*"*46)
        return (200,"Ok")
    elif(len(err)!=0):
        print("Some checks failed")
        print("*" * 46)
        return (500,err)
    else:
        print("Found some failed Iflows")
        print("*" * 46)
        return (201,result)
