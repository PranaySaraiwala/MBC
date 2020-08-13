import flask
import requests
import json
from flask import make_response
from flask import jsonify


app = flask.Flask(__name__)
app.config["DEBUG"] = True

import os

port = int(os.getenv("PORT", 9009))


@app.route('/', methods=['GET'])
def home():
    return "<h1>MBC Iflow Monitoring</h1><p>This site is an API to check Iflow's in error in all MBC tenants</p>"




@app.route('/api/v1/mbc/cluster1', methods=['GET'])  # Cluser name
def cluster1():
    flag = 0
    url = "https://P1941374267:*******@api.eu3.hana.ondemand.com/monitoring/v1/accounts/ae078c012/dbsystem/jta/metrics"
    response = requests.request("GET", url)
    data = json.loads(response.content)
    payload = data[0]
    replication_data = payload["metrics"]
    if response.status_code == 200:
        for data_set in replication_data:
            if (data_set['name'] == 'HANA Replication Status Check'):
                if (data_set['output'] == "Primary replication: ACTIVE"):
                    return make_response(jsonify({'Replication attached': 'AMS to ROT'}), 200)
                    flag = 1
                else:
                    return make_response(jsonify({'error': 'Not found'}), 404)
    else:
        return make_response(jsonify({'error': 'API down'}), 404)

    if flag == 0:
        return make_response(jsonify({'error': 'Not Found'}), 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
