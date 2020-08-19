import json
import requests
from common.Auth import *

def download_delta(id,_path):
    data = []
    part = _path.rpartition("/")
    try:
        r = requests.get(_path, headers=hder)
        print("\nFetching results from "+id+str(r))
        results = json.loads(r.text)
        data.append(results['d']['results'])
        if "__next" in results['d']:
            download_next_log_delta(data,part, results['d']['__next'], results['d']['__count'])
        return data
    except Exception as e:
        print(e)
        print("Cannot fetch Logs from "+_path)
        raise Exception()

def download_next_log_delta(data,part, next_path, total_count):
    part=part[0].rpartition("/")
    iterations = int(total_count) // 1000
    for j in range(iterations):
        r = requests.get(part[0] + part[1] + next_path, headers=hder)
        results = json.loads(r.text)
        data.append(results['d']['results'])
        if "__next" in results['d']:
            next_path = results['d']['__next']
