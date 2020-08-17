
from ErrorIflowCheck import *
from Bank_List import *
def jsonifyData(data):
    x = {}
    for i, j in data.items():
        count = 0
        if j[0] != "Ok":
            print(j)

            x.update({str(count):{}})
            x[str(count)].update({"Name": j[2]})
            x[str(count)].update({"Url": j[3]})
            x[str(count)].update({"Count": j[1]})
            x[str(count)].update({"IflowDetails": []})
            for k in range(4, len(j)):
                x[str(count)]["IflowDetails"].append({"Id": j[k][0],"Version": j[k][1],"Name": j[k][2]})
        count+=1
    return x

x=main(eu2Tenants)

json_data = (json.dumps(jsonifyData(x[1]), sort_keys=False, indent=4, separators=(',', ': ')))
print(json_data)