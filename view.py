from flask import Flask,make_response,jsonify
from model import *
from common.cluster import *

def logic(cluster,type):
    res = main(cluster,type)
    if(res[0]==200):
        return make_response(jsonify({'Status': 'Ok'}), 200)

    elif(res[0]==500):
        return make_response(jsonify(prepareData(res[1],500)), 500)
    else:
        return make_response(jsonify(res[1]), 201)

app=Flask(__name__)
app.config["DEBUG"] = True

import os

port = int(os.getenv("PORT", 9010))


@app.route('/', methods=['GET'])
def home():
    return "<h1>MBC Iflow and Tenant Runtime Monitoring</h1><p>This site is an API to check artifact status and runtime status of MBC tenants</p>"


@app.route('/api/v1/mbc/<index>', methods=['GET'])
def iflowCheck(index):
    return logic(cluster[index],"iflow")


@app.route('/api/v1/mbc/rt/<index>', methods=['GET'])
def runtimeCheck(index):
    return logic(cluster[index],"runtime")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
