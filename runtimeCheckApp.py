from flask import Flask,make_response,jsonify
from runtimeAvailability import *
from common.runtimeCluster import *
import os

def logic(cluster):
    res = main(cluster)
    if(res[0]==200):
        return make_response(jsonify({'Status': 'Ok'}), 200)
    elif(res[0]==500):
        return make_response(jsonify(prepareData(res[1],500)), 500)
    else:
        return make_response(jsonify(prepareData(res[1],201)), 201)

app=Flask(__name__)
app.config["DEBUG"] = True

port = int(os.getenv("PORT", 9011))

@app.route('/', methods=['GET'])
def home():
    return "<h1>MBC Tenant Runtime Monitoring</h1><p>This site is an API to check Runtime Availability of all MBC tenants</p>"

@app.route('/api/v1/mbc/rt/PR301', methods=['GET'])  # API name for PR301 tenants
def PR301():
    return logic(PR301_500049309)

@app.route('/api/v1/mbc/rt/PR302', methods=['GET'])  # API name for PR302 tenants
def PR302():
    return logic(PR302_500054753)

@app.route('/api/v1/mbc/rt/PR303', methods=['GET'])  # API name for PR303 tenants
def PR303():
    return logic(PR303_500163845)

@app.route('/api/v1/mbc/rt/PR304', methods=['GET'])  # API name for PR304 tenants
def PR304():
    return logic(PR304_500172688)

@app.route('/api/v1/mbc/rt/PR002', methods=['GET'])  # API name for PR002 tenants
def PR002():
    return logic(PR002_500186492)

@app.route('/api/v1/mbc/rt/PR003', methods=['GET'])  # API name for PR003 tenants
def PR003():
    return logic(PR003_500189364)

@app.route('/api/v1/mbc/rt/PR102', methods=['GET'])  # API name for PR102 tenants
def PR102():
    return logic(PR102_500049440)

@app.route('/api/v1/mbc/rt/PR103', methods=['GET'])  # API name for PR103 tenants
def PR103():
    return logic(PR103_500186493)

@app.route('/api/v1/mbc/rt/PR202', methods=['GET'])  # API name for PR202 tenants
def PR202():
    return logic(PR202_500186494)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
