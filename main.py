from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
import time
import os
import selenium.webdriver.support.expected_conditions as ec
from zip_codes import states_dict
from database import db_connect_and_create, db_load_zip_lists, db_add_bad_zip, db_add_region_data
from scraper import Scraper

#TODO move zip code list to database
scraper = Scraper()
db_connect_and_create()
bad_zip_list, good_zip_list = db_load_zip_lists()
state = 'United States'
zip_code_list = states_dict[state]
driver, wait = scraper.driver, scraper.wait
scraper.login()
for zip_code in zip_code_list:    
    if zip_code not in bad_zip_list and zip_code not in good_zip_list:
        while True:
            try:
                driver.get(f'https://www.redfin.com/zipcode/{zip_code}/filter/include=sold-5yr')
                #driver.get(f'https://www.redfin.com/stingray/api/gis-csv?al=2&has_deal=false&has_dishwasher=false&has_laundry_facility=false&has_laundry_hookups=false&has_parking=false&has_pool=false&has_short_term_lease=false&include_pending_homes=false&isRentals=false&is_furnished=false&market={state.lower()}num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id=22614&region_type=2&sold_within_days=1825&status=9&travel_with_traffic=false&travel_within_region=false&uipt=1,2,3,4,5,6,7,8&utilities_included=false&v=8')
                time.sleep(2)

                #checks if zip code url is bad, adds to bad zip codes db
                if driver.current_url == 'https://www.redfin.com/sitemap' or driver.current_url == 'https://www.redfin.com/404':
                    db_add_bad_zip(zip_code)
                    break
                
                #waits for map to load before getting data
                else:
                    dict = driver.execute_script('return dataLayerInitializationValues')
                    params = (dict['region_id'], dict['session']['searchMarket'], dict['region_type_id'], zip_code)
                    db_add_region_data(params)
                    break
            except (TimeoutException, WebDriverException):
                pass