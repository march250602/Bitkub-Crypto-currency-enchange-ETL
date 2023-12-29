import hashlib
import hmac
import json
import time
import requests
import urllib3
import pandas as pd
import s3fs

urllib3.disable_warnings()

def gen_sign(api_secret, payload_string=None):
    return hmac.new(api_secret.encode('utf-8'), payload_string.encode('utf-8'), hashlib.sha256).hexdigest()

def gen_query_param(url, query_param):
    req = requests.PreparedRequest()
    req.prepare_url(url, query_param)
    return req.url.replace(url,"")


def Bitkub_etl():
    if __name__ != '__main__':
        
        host = 'https://api.bitkub.com'
        path = '/api/market/ticker'
        api_key = 'your api_key'
        api_secret = 'your api_secret'
        
        ts = str(round(time.time() * 1000))
        param = {
            'sym':"THB_BTC"
        }
        req = requests.PreparedRequest()
        req.prepare_url(host+path, param)
        query_param = req.url.replace(host+path,"")

        payload = []
        payload.append(ts)
        payload.append('GET')
        payload.append(path)
        payload.append(query_param)

        sig = gen_sign(api_secret, ''.join(payload))
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-BTK-TIMESTAMP': ts,
            'X-BTK-SIGN': sig,
            'X-BTK-APIKEY': api_key
        }

        response = requests.request('GET', f'{host}{path}{query_param}', headers=headers, data={}, verify=False)
        Jasonformat=response.json()
        

        data_dict = Jasonformat["THB_BTC"]

        list=[data_dict]
        df = pd.DataFrame(list)
        df.to_csv('s3://mybitkub-etl/Bitkub.csv')
        
