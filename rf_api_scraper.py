import requests
import json
from database import *
import time
from threading import Thread
import pandas as pd
from io import StringIO
from datetime import date

#TODO Continue loading regions and data
#TODO Add logic to add last updated to each region
#TODO Docstrings, comments

#for_sale_url = f'https://www.redfin.com/stingray/api/gis-csv?al=2&has_deal=false&has_dishwasher=false&has_laundry_facility=false&has_laundry_hookups=false&has_parking=false&has_pool=false&has_short_term_lease=false&include_pending_homes=false&isRentals=false&is_furnished=false&num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type={region_type_id}&status=9&travel_with_traffic=false&travel_within_region=false&uipt=1,2,3,4,5,6,7,8&utilities_included=false&v=8'
def read_data(id, region_type_id):
    resp = requests.get(f'https://www.redfin.com/stingray/do/query-regionid?region_id={id}&region_type={region_type_id}')
    resp.raise_for_status()
    resp_json = json.loads(resp.text.replace('{}&&', ''))

    
    if resp_json['resultCode'] == 0:
        params = (resp_json.get('payload').get('regions')[0].get('id').get('tableId'),
                resp_json.get('payload').get('regions')[0].get('id').get('type'),
                id,
                resp_json.get('payload').get('regions')[0].get('name'),
                resp_json.get('payload').get('regions')[0].get('cleanedName'),
                resp_json.get('payload').get('regions')[0].get('market'),
                resp_json.get('payload').get('regions')[0].get('market_id'),
                resp_json.get('payload').get('regions')[0].get('market_display_name'),
                resp_json.get('payload').get('regions')[0].get('url'),
                resp_json.get('payload').get('regions')[0].get('polygon'),
                resp_json.get('payload').get('regions')[0].get('isBoundingBox'),
                resp_json.get('payload').get('isRedfinServiced'))
        print(resp_json)
        print(params)
        db_add_new_region_data(params)
    else:
        print(id)
        params = (id, region_type_id)
        db_add_tested_ids(params)

def dl_csv(region_id, region_type_id):
    #https://www.redfin.com/stingray/api/gis-csv?al=2&include_pending_homes=false&isRentals=false&num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id=1&region_type=1&sold_within_days=18250&status=9&uipt=1,2,3,4,5,6,7,8&v=8
    searched = db_sold_searched()
    if (region_id, region_type_id) not in searched:

        sold_dl_url = f'https://www.redfin.com/stingray/api/gis-csv?al=1&include_pending_homes=false&isRentals=false&num_homes=35000&ord=last-sale-date-desc&page_number=1&region_id={region_id}&region_type={region_type_id}&sold_within_days=18250&status=9&uipt=1,2,3,4,5,6,7,8&v=8'
        resp = requests.get(sold_dl_url)
        resp.raise_for_status()
        text = resp.text
        #print(region_id, region_type_id)
        csv_text = StringIO(text)
        csv_df = pd.read_csv(csv_text)
        if csv_df.shape[0] > 8000:
            print(region_id, region_type_id)
        if csv_df.shape[0] == 0:
            print(region_id, region_type_id)
            params = [None for _ in range(0,24)]
            params.append(-100 * (region_id))
            params.append(region_id),
            params.append(region_type_id)
            print(params)
            db_add_sold_data(params)

        for (_, series) in csv_df.iterrows():
            try:
                sold_date = date.strptime(series.get('SOLD DATE'), format = "%B-%d-%Y")
                year= sold_date.year
                day = sold_date.day
                month = sold_date.month
            except TypeError:
                sold_date = None 
                month = None
                day = None
                year = None
                series.get('SOLD DATE')
            params = (series.get('SALE TYPE'),
                    sold_date,
                    series.get('PROPERTY TYPE'),
                    series.get('ADDRESS'),
                    series.get('CITY'),
                    series.get('STATE OR PROVINCE'),
                    series.get('ZIP OR POSTAL CODE'),
                    series.get('PRICE'),
                    series.get('BEDS'),
                    series.get('BATHS'),
                    series.get('LOCATION'),
                    series.get("SQUARE FEET"),
                    series.get("LOT SIZE"),
                    series.get('YEAR BUILT'),
                    series.get('DAYS ON MARKET'),
                    series.get('$/SQUARE FEET'),
                    series.get('HOA/MONTH'),
                    series.get('STATUS'),
                    series.get('NEXT OPEN HOUSE START TIME'),
                    series.get('NEXT OPEN HOUSE END TIME'),
                    series.get('URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)'),
                    series.get('SOURCE'),
                    series.get('MLS#'),
                    series.get('LATITUDE'),
                    series.get('LONGITUDE'),
                    region_id,
                    region_type_id,
                    year,
                    month,
                    day
                    )
            db_add_sold_data(params)


db_connect_and_create()
'''
region_types = [num for num in range(1,12)]
region_range = [num for num in range(1,1000000)]
region_type_id = 1

tested = db_load_tested(region_type_id=region_type_id)
region_range = list(set(region_range) - set(tested))
for id in region_range:
    thread = Thread(target=read_data, args=[id, region_type_id])
    thread.start()
    time.sleep(.201)
'''           
valid_table = db_load_valid(1)
print(valid_table)
for row in valid_table:
    #print(row)
    region_id = row[0]
    region_type_id = row[1]
    dl_csv(region_id, region_type_id)
    # thread = Thread(target=dl_csv, args=[region_id, region_type_id])
    #thread.start()
    time.sleep(.2)

    