import requests
import json
from database import db_connect_and_create, db_add_new_region_data, db_add_tested_ids, db_load_tested
import time
from threading import Thread

def try_or_undefined(func,id):
    if func() == None:
        return f'undefined{id}'
    else:
        return func()
    
def try_or_neg_one(func):
    try:
        return func()
    except KeyError:
        return -(id)

def read_data(id):
    resp = requests.get(f'https://www.redfin.com/stingray/do/query-regionid?region_id={id}&region_type=1')
    resp.raise_for_status()
    resp_json = json.loads(resp.text.replace('{}&&', ''))
    if resp_json['resultCode'] == 0:
        params = (resp_json['payload']['regions'][0]['id']['tableId'],
                resp_json['payload']['regions'][0]['id']['type'],
                resp_json['payload']['regions'][0]['name'],
                resp_json['payload']['regions'][0]['cleanedName'],
                resp_json.get('payload').get('regions')[0].get('market', id),
                resp_json.get('payload').get('regions')[0].get('market_id', id),
                resp_json.get('payload').get('regions')[0].get('market_display_name', id),
                resp_json.get('payload').get('regions')[0].get('url'),
                resp_json['payload']['isRedfinServiced'])
        #print(resp_json['payload']['regions'][0]['id']['tableId'])
        print(params)
        db_add_new_region_data(params)
    else:
        print(id)
        params = (id, 1)
        db_add_tested_ids(params)

db_connect_and_create()
region_types = [num for num in range(1,12)]
region_range = [num for num in range(1,100000)]

tested = db_load_tested()
region_range = list(set(region_range) - set(tested))
for id in region_range:
    thread = Thread(target=read_data, args=[id])
    thread.start()
    time.sleep(.2)
            