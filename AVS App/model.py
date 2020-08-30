# coding=utf-8
import threading
from common import *
import json
import requests

def callThreads(tList):
    #starts each thread
    for i in tList:
        i.start()
    #joins each thread
    for i in tList:
        i.join()

def createJson(list,header,value):
    tup = zip(header, value)
    dic = {}
    for i, j in tup:
        dic[i] = j
    list.append(dic)

def artifactData(id,name,home,result,data,flag):
    errorCount = int(data["d"]["__count"])
    baseHeader=["Tenant","IflowCount","Customer","Home","IflowDetails"]

    if (errorCount != 0):
        Data = [id, errorCount, name, home,[]]
        flag.add("Error")
        for d in data["d"]["results"]:
            Data[-1].append({'Id':d["Id"],'Version':d["Version"],'Name':d["Name"]})
            createJson(result,baseHeader,Data)

def healthData(id,name,home,result,data,flag):
    baseHeader = ["Tenant", "HealthStatus", "Customer", "Home"]
    if (data != 200):
        Data=[id,data,name,home]
        createJson(result,baseHeader,Data)
        flag.add("Error")

def connectionCheck(id,tenantUrl,home,name,checkUrl,result,err,flag,type):


    try:
        print("Requesting Status from " +id)
        r = requests.get(tenantUrl + checkUrl, headers=hder)

        if type == "iflow":
            response = json.loads(r.text)
            artifactData(id,name,home,result,response,flag)

        else:
            healthData(id,name,home,result,r.status_code,flag)

    except Exception as e:
        print(e)
        print("Cannot fetch result from " + id)
        header=["Tenant","Error","Customer","Home"]
        data=[id,str(e),name,home]
        createJson(err,header,data)

def main(tenantList,type):
    flag = set()
    result = []
    err = []
    threadList = []

    #API Urls to call
    iflowcheckUrl = ".hana.ondemand.com/api/v1/IntegrationRuntimeArtifacts/?$inlinecount=allpages&$filter=Status eq 'ERROR' or Status eq 'FAILED'"
    runtimecheckUrl=".hana.ondemand.com/http/health"
    homeurl = ".hana.ondemand.com/itspaces/shell/monitoring/Overview"

    for id, value in tenantList.items():
        if(type=="iflow"):
            tenantUrl=value[1]
            checkUrl=iflowcheckUrl
            home=tenantUrl+homeurl
        else:
            tenantUrl = value[0]
            checkUrl = runtimecheckUrl
            home=tenantUrl+homeurl

        #Creating a thread for each of the tenants
        threadList.append(threading.Thread(target=connectionCheck,args=(id,tenantUrl,home,value[2],checkUrl,result,err,flag,type)))

    callThreads(threadList)

    #execution resumes here once all threads have completed executing.

    print("*"*20+"RESULT"+"*"*20)

    if(len(flag)==0 and len(err)==0):
        return (200,"Ok")
    elif(len(err)!=0):
        print("Some checks failed")
        return (500,result,err)
    else:
        return (201,result)
