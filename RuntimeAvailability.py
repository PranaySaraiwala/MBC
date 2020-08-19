# coding=utf-8
import threading
from common.Auth import *
import json
import requests


def prepareData(data):
    x = {}
    for i, j in data.items():
        count = 0
        if j[0] != "Ok":

            x.update({str(count):{}})
            x[str(count)].update({'Name': j[2]})
            x[str(count)].update({'Url': j[3]})
            x[str(count)].update({'Count': j[1]})
            x[str(count)].update({'IflowDetails': []})
            for k in range(4, len(j)):
                x[str(count)]['IflowDetails'].append({'Id': j[k][0],'Version': j[k][1],'Name': j[k][2]})
        count+=1
    return x

def prepareErrorData(data):
    x = {}
    for i, j in data.items():
        count = 0

        x.update({str(count): {}})
        x[str(count)].update({'Id': j[0]})
        x[str(count)].update({'Error': j[1]})
        x[str(count)].update({'Url': j[2]})
        count += 1
    return x

def main(tenantList):
    print(type(tenantList))
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
        home=".hana.ondemand.com/itspaces/shell/monitoring/Overview"

        try:
            print("Requesting Status from " +id)
            r = requests.get(tenantUrl + checkUrl, headers=hder)
            response = json.loads(r.text)
            errorCount = int(response["d"]["__count"])
            if (errorCount == 0):
                result.update({id: ["Ok"]})
                #result.update({id: [id,"Ok"]})

            else:
                flag = 1
                for data in response["d"]["results"]:
                    uData = [data["Id"], data["Version"], data["Name"]]
                    sData = [str(x) for x in uData]

                    if (result.get(id) == None):
                        result.update({id: ["Error", errorCount, name, tenantUrl + home]})

                        result[id].append(sData)

                    else:
                        result[id].append(sData)


        except Exception as e:
            print(e)
            print("Cannot fetch result from " +id)
            err.update({id:[id,str(e),tenantUrl+home]})


    for id, value in tenantList.items():
        #Creating a thread for each of the tenants
        threadList.append(threading.Thread(target=connectionCheck,args=(id,value[0],value[1],checkUrl,)))

    callThreads(threadList)

    #execution resumes here once all threads have completed executing.

    print("All Threads Completed\n")
    print("*"*50+"RESULT"+"*"*50)

    if(flag==0 and len(err)==0):
        print("No Failed Iflows")
        return (200,"Ok")
    elif(len(err)!=0):
        print("Some checks failed")
        return (201,err)
        # for key,val in err.items():
        #     print (key,val)
    else:
        return (202,result)

