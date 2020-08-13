# coding=utf-8
from Bank_List import *
import threading
import json
import requests
from Auth import *

import csv

class checkConnection (threading.Thread):
    iflowData={}
    err=[]
    eFlag=0


    def __init__(self,tenantId,tenantUrl,customerName,iflowStatus):
        threading.Thread.__init__(self)
        self.id=tenantId
        self.url=tenantUrl
        self.name=customerName
        self.iflStatus=iflowStatus
        self.home=".hana.ondemand.com/itspaces/shell/monitoring/Overview"

#dataformat = Tenant ID: [Status,IflowCount,CustomerName,URL,IflowDetails]
    def run(self,):
        try:
            print("Requesting Status from "+self.id)
            r = requests.get(self.url + iflowStatus, headers=hder)
            response = json.loads(r.text)
            errorCount=int(response["d"]["__count"])
            if(errorCount==0):
                checkConnection.iflowData.update({self.id:["Ok"]})
                #checkConnection.iflowData[self.id].extend([0,self.name,self.url+self.home])


            else:
                checkConnection.eFlag=1
                for data in response["d"]["results"]:
                    uData=[data["Id"],data["Version"],data["Name"]]
                    sData=[str(x) for x in uData]
                if(checkConnection.iflowData.get(self.id)==None):
                    checkConnection.iflowData.update({self.id:["Error",errorCount,self.name,self.url+self.home]})
                    checkConnection.iflowData[self.id].append(sData)
                else:
                    checkConnection.iflowData[self.id].append(sData)

        except Exception as e:
            print(e)
            print("Cannot fetch result from " + self.id)
            checkConnection.err.append([self.id,e])

#API Urls to call
iflowStatus = ".hana.ondemand.com/api/v1/IntegrationRuntimeArtifacts/?$inlinecount=allpages&$filter=Status eq 'ERROR' or Status eq 'FAILED'"

#Stores the list of threads created for each tenant
threadList=[]

for id, value in eu2Tenants.items():
    #Creating a thread for each of the tenants
    threadList.append(checkConnection(id,value[0],value[1],iflowStatus))

#Starts each thread and then joins them
for i in threadList:
    i.start()
for i in threadList:
    i.join()


#execution resumes here once all threads have completed executing.

print("All Threads Completed")
status=checkConnection.iflowData
err=checkConnection.err
flag=checkConnection.eFlag

if(flag==0 and len(err)==0):
    exit(0)
elif(len(err)!=0):
    print("Some checks failed")
    for i in err:
        print (i)
else:
    print("Tenant\tIflowID\tIflowVersion\tIflowName\n")
    for i, j in status.items():
        if j[0]!="Ok":
            print("Customer Name= " + j[2])
            print("\tNo Of Iflows in Error= "+str(j[1]))
            print("\tTenant URL= "+j[3])









# with open('Logs.csv',"w",) as csv_file:
#         d_writer = csv.writer(csv_file)
#         header = ["Tenant", "Client","Total Message count","FailedEscalated"]
#         d_writer.writerow(header)
#         d_writer.writerows(dataCount)