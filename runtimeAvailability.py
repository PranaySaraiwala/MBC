# coding=utf-8
import threading
from common.auth import *
import json
import requests
def prepareData(data,code):
    x = {}
    for i, j in data.items():
        if code!=500:
            if j['Status'] !=200:
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
    checkUrl = '.hana.ondemand.com/http/health'

    def callThreads(tList):
        #starts each thread
        for i in tList:
            i.start()
        #joins each thread
        for i in tList:
            i.join()

    def connectionCheck(id,tenantUrl,name,checkUrl):
        nonlocal flag,result,err
        home=".hana.ondemand.com/itspaces/shell/monitoring/Overview"
        try:
            response = requests.get(tenantUrl + checkUrl, headers=hder)
            print("Runtime status of " +id+" is: ",response.status_code)
            tenant=tenantUrl.replace('ifl.snsp','tmn.snw')
            result.update({id: {'Status':response.status_code,'Customer':name,'Tenant':tenant+home}})
            if (response.status_code!=200):
                flag=1
        except Exception as e:
            print(e)
            print("Cannot fetch result from " +id)
            err.update({id:{'Status':'Error','Error':str(e),'Tenant':tenant+home}})

    for id, value in tenantList.items():
        #Creating a thread for each of the tenants
        threadList.append(threading.Thread(target=connectionCheck,args=(id,value[0],value[1],checkUrl,)))

    callThreads(threadList)
    #execution resumes here once all threads have completed executing.
    print("*"*15+" RESULT "+"*"*15)

    if(flag==0 and len(err)==0):
        print("No Runtime Error")
        return (200,"Ok")
    elif(len(err)!=0):
        print("Some Checks Failed")
        return (500,err)
    else:
        return (201,result)