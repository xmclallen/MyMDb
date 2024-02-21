from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime, timedelta
import time
 

app = Flask(__name__)

def lookupUPC(upc):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip,deflate',
        #'user_key': 'only_for_dev_or_pro',
        #'key_type': '3scale'
    }
    resp = requests.get(f"https://api.upcitemdb.com/prod/trial/lookup?upc={upc}", headers=headers)
    data = json.loads(resp.text)
    headers = resp.headers

    ini_time_for_now = datetime.now()
    print(f"Warning - UPC DB API limit remaining is: {headers['X-RateLimit-Remaining']}")
    reset_time = headers['X-RateLimit-Reset']
    now = time.time()
    diff = float(reset_time) - now
    diff_str = datetime.fromtimestamp(diff / 1000).strftime('%Hh %Mm %Ss')
    print(f"        - UPC DB API limit resets in: {diff_str}\n")

    item = data['items'][0]
    response = {
        upc : {
            'ean' : item['ean'], 
            'title' : item['title'], 
            'image' : item['images'][0]
        }
    }

    return response

movie_colletion = {}

@app.route('/catalogUPC', methods=['GET'])
def catalogUPC():

    upc_str = request.args.get('text', '')
    print(f"Looking up UPC in movie database: {upc_str} ...")
    new_movie = lookupUPC(upc_str)
    print(new_movie)

    print("\nAdding item to MyMDb collection ...")
    movie_colletion.update(new_movie)

    with open('myMDb.json', 'w') as fp:
        json.dump(movie_colletion, fp)    

    return new_movie

if __name__ == '__main__':
    app.run(host='0.0.0.0')
