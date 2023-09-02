from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
import time
from itertools import zip_longest
import selenium.webdriver.support.expected_conditions as ec
from zip_codes import states_dict
from database import db_connect_and_create, db_load_zip_lists, db_add_bad_zip, db_add_region_data
from scraper import Scraper

#splits iterable into n seperate lists, fills extra with padvalue
def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

#TODO move zip code list to database
scraper_list = [Scraper() for _ in range(0,5)]
#scraper = Scraper()
db_connect_and_create()
bad_zip_list, good_zip_list = db_load_zip_lists()
state = 'United States'
zip_code_list = states_dict[state]
#driver, wait = scraper.driver, scraper.wait
for scraper in scraper_list:
    scraper.login()
zip_list = list(set(zip_code_list) - set(good_zip_list) - set(bad_zip_list))    
zip_list = grouper(5, zip_list)
for zip_tuple in zip_list:
    for zip_code, scraper in zip(zip_tuple, scraper_list):
        while True:
            try:
                print("%05d" % (zip_code,))
                print(f'https://www.redfin.com/zipcode/{"%05d" % (zip_code)}/filter/include=sold-5yr')
                scraper.driver.get(f'https://www.redfin.com/zipcode/{"%05d" % (zip_code)}/filter/include=sold-5yr')
                #driver.get(f'https://www.redfin.com/stingray/api/gis-csv?al=2&has_deal=false&has_dishwasher=false&has_laundry_facility=false&has_laundry_hookups=false&has_parking=false&has_pool=false&has_short_term_lease=false&include_pending_homes=false&isRentals=false&is_furnished=false&market={state.lower()}num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id=22614&region_type=2&sold_within_days=1825&status=9&travel_with_traffic=false&travel_within_region=false&uipt=1,2,3,4,5,6,7,8&utilities_included=false&v=8')
                time.sleep(2)
                break
            
            except (TimeoutException, WebDriverException):
                pass
    for zip_code, scraper in zip(zip_tuple, scraper_list):
        while True:
            try:
                #checks if zip code url is bad, adds to bad zip codes db
                if scraper.driver.current_url == 'https://www.redfin.com/sitemap' or scraper.driver.current_url == 'https://www.redfin.com/404':
                    db_add_bad_zip(zip_code)
                    break
                
                #loads data from script, adds to db
                else:
                    dict = scraper.driver.execute_script('return dataLayerInitializationValues')
                    market = scraper.driver.execute_script('return searchMarket')
                    params = (dict['region_id'], market, dict['region_type_id'], zip_code)
                    print(params)
                    db_add_region_data(params)
                    break
            except (TimeoutError, NoSuchElementException):
                pass