import requests, json
print(requests.get('https://192.168.17.39:3002/api/ibalam/ns=3;s=V:0.3.0.0.5', verify=False).json()['data']['value'])