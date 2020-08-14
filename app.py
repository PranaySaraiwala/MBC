from flask import Flask
from flask import make_response
from flask import jsonify
from ErrorIflowCheck import *
from cluster import *
#from Bank_List import *

def logic(cluster):
    res = main(cluster)
    if(res[0]==200):
        return make_response(jsonify({'Status': 'Ok'}), 200)

    elif(res[0]==201):
        return make_response(jsonify(res[1]), 500)
    else:
        x=jsonifyData(res[1])
        return make_response(jsonify(x),201)

def jsonifyData(data):
    x = {}
    for i, j in data.items():
        count = 0
        if j[0] != "Ok":

            x.update({str(count):{}})
            x[str(count)].update({'Name': str(j[2])})
            x[str(count)].update({'Url': str(j[3])})
            x[str(count)].update({'Count': str(j[1])})
            x[str(count)].update({'IflowDetails': []})
            for k in range(4, len(j)):
                x[str(count)]['IflowDetails'].append({'Id': str(j[k][0]),'Version': str(j[k][1]),'Name': str(j[k][2])})
        count+=1
    return x


app=Flask(__name__)
app.config["DEBUG"] = True

import os

port = int(os.getenv("PORT", 9009))


@app.route('/', methods=['GET'])
def home():
    return "<h1>MBC Iflow Monitoring</h1><p>This site is an API to check Iflow's in error in all MBC tenants</p>"


@app.route('/api/v1/mbc/PR301', methods=['GET'])  # API name for PR301 tenants
def PR301():
    return logic(PR301_500049309)

@app.route('/api/v1/mbc/PR302', methods=['GET'])  # API name for PR302 tenants
def PR302():
    return logic(PR302_500054753)

@app.route('/api/v1/mbc/PR303', methods=['GET'])  # API name for PR303 tenants
def PR303():
    return logic(PR303_500163845)

@app.route('/api/v1/mbc/PR304', methods=['GET'])  # API name for PR304 tenants
def PR304():
    return logic(PR304_500172688)


#Tenant list as configured in Banklist.py

# @app.route('/api/v1/mbc/eu2', methods=['GET'])  # API name to check all eu2 tenants
# def eu2():
#     return logic(eu2Tenants)
#
# @app.route('/api/v1/mbc/eu1', methods=['GET'])  # API name to check all eu1 tenants
# def eu1():
#     return logic(eu1Tenants)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
