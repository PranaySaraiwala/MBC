# Change Line 132 based on python version (2.7 or 3.6)
from Bank_List import *
from pckg import *
import threading
from datetime import datetime, timedelta
import csv



class checkConnection (threading.Thread):
    datacount=[]
    def __init__(self,tenantId,tenantUrl,customerName,totalMpl,failedEscalatedMpl):
        threading.Thread.__init__(self)

        self.id=tenantId
        self.url=tenantUrl
        self.name=customerName
        self.totalMpl=totalMpl
        self.failedEscalatedMpl=failedEscalatedMpl

    def run(self):
        try:

            r = requests.get(self.url + totalMpl, headers=hder)
            #print("\nchecking totalMpl with "+self.id+"\t"+self.name+"\t")
            totalCount = json.loads(r.text)

            r = requests.get(self.url + failedEscalatedMpl, headers=hder)
            #print("\nchecking failedEscalatedMpl with " + self.id + "\t" + self.name + "\t")
            failedEscalatedCount = json.loads(r.text)
            dataCount.append([self.id, self.name, totalCount, failedEscalatedCount])
            print (threading.active_count())
            print("\n")
            #dataCount.append([id_, value_[1], totalCount['d']['__count'], failedEscalatedCount['d']['__count']])

        except Exception as e:
            print(e)
            print("Cannot fetch Logs from " + self.id)







dataCount = []

totalMpl = ".hana.ondemand.com/api/v1/MessageProcessingLogs/$count"
failedEscalatedMpl=".hana.ondemand.com/api/v1/MessageProcessingLogs/$count?$filter=(Status eq 'FAILED' or Status eq 'ESCALATED')"
threadList=[]
for id, value in Tenant_Id.items():
    # log_resp... will be a list  where each of its element will be a list of responses for a tenant.
    threadList.append(checkConnection(id,value[0],value[1],totalMpl,failedEscalatedMpl))

for i in threadList:
    i.start()

for i in threadList:
    i.join()



print("Tenant\tName\tTotalMessage\tTotalFailedEscalated\n")
for i in dataCount:
    print(i)

print("final")
print(threading.active_count())
if (threading.active_count()==0):
    dataCount=checkConnection.datacount

with open('Logs.csv',"w",) as csv_file:
        d_writer = csv.writer(csv_file)
        header = ["Tenant", "Client","Total Message count","FailedEscalated"]
        d_writer.writerow(header)
        d_writer.writerows(dataCount)