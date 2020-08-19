from flask import Flask
from flask import make_response
from flask import jsonify
from ErrorIflowCheck import *
from common.cluster import *
#from Bank_List import *

def logic(cluster):
    res = main(cluster)
    if(res[0]==200):
        return make_response(jsonify({'Status': 'Ok'}), 200)

    elif(res[0]==201):
        return make_response(jsonify(prepareErrorData(res[1])), 500)
    else:
        # return make_response(json.dumps(prepareData(res[1]), sort_keys=False, indent=4, separators=(',', ': ')),201)
        return make_response(jsonify(prepareData(res[1])), 201)

app=Flask(__name__)
app.config["DEBUG"] = True

import os

port = int(os.getenv("PORT", 9010))


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

@app.route('/api/v1/mbc/PR002', methods=['GET'])  # API name for PR002 tenants
def PR002():
    return logic(PR002_500186492)

@app.route('/api/v1/mbc/PR003', methods=['GET'])  # API name for PR003 tenants
def PR003():
    return logic(PR003_500189364)

@app.route('/api/v1/mbc/PR102', methods=['GET'])  # API name for PR102 tenants
def PR102():
    return logic(PR102_500049440)

@app.route('/api/v1/mbc/PR103', methods=['GET'])  # API name for PR103 tenants
def PR103():
    return logic(PR103_500186493)

@app.route('/api/v1/mbc/PR202', methods=['GET'])  # API name for PR202 tenants
def PR202():
    return logic(PR202_500186494)


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
