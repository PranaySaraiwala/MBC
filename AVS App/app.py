from flask import Flask,make_response,jsonify,render_template
from model import *
import os

def logic(cluster,type):
    res = main(cluster,type)
    if res[0] ==200:
        return make_response(jsonify({'Status': 'Ok'}), 200)
    elif res[0]==500:
        print(res[1])
        print(res[2])
        return render_template("result.html",result=res[1],err=res[2],length=len(res[2]),view=type)
    else:
        print(res[1])
        return render_template("result.html", result=res[1], err=[], length=0,view=type)

app=Flask(__name__)
app.config["DEBUG"] = True

port = int(os.getenv("PORT", 9011))

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