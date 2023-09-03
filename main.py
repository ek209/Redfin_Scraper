from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
from threading import Thread
from itertools import zip_longest
from zip_codes import states_dict
from database import db_connect_and_create, db_load_zip_lists, db_add_bad_zip, db_add_region_data
from scraper import Scraper

#splits iterable into n seperate lists, fills extra with padvalue
def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def scrape_zip(scraper, zip_code):
    """Uses a Scraper's driver to load the webpage with the zip code.
    Loops through in case of webpage loading issue.

    Args:
        scraper (Scraper): Scraper used to search.
        zip_code (Int): Zip used to search
    """
    while True:
        try:
            scraper.driver.get(f'https://www.redfin.com/zipcode/{"%05d" % (zip_code)}/filter/include=sold-5yr')
            #driver.get(f'https://www.redfin.com/stingray/api/gis-csv?al=2&has_deal=false&has_dishwasher=false&has_laundry_facility=false&has_laundry_hookups=false&has_parking=false&has_pool=false&has_short_term_lease=false&include_pending_homes=false&isRentals=false&is_furnished=false&market={state.lower()}num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id=22614&region_type=2&sold_within_days=1825&status=9&travel_with_traffic=false&travel_within_region=false&uipt=1,2,3,4,5,6,7,8&utilities_included=false&v=8')
            time.sleep(2)
            break
        except (TimeoutException, WebDriverException, NoSuchElementException):
            pass

def get_region_id(scraper, zip_code):
    """Adds the zip code to either bad zip code table or to region table
    based on data grabbed from scraper driver. Loops through in case of loading error.

    Args:
        scraper (Scraper): Scraper object to scrape webpage data from driver
        zip_code (Int): Zip code to add to database

    Returns:
        Nothing
    """
    while True:
        try:
            if scraper.driver.current_url == 'https://www.redfin.com/sitemap' or scraper.driver.current_url == 'https://www.redfin.com/404':
                db_add_bad_zip(zip_code)
                break
            
            else:
                dict = scraper.driver.execute_script('return dataLayerInitializationValues')
                market = scraper.driver.execute_script('return searchMarket')
                params = (dict['region_id'], market, dict['region_type_id'], zip_code)
                print(params)
                db_add_region_data(params)
                break
        except (TimeoutException, WebDriverException, NoSuchElementException):
            pass


#TODO move zip code list to database
scraper_count = 6
thread_list = []
scraper_list = [Scraper() for _ in range(0,scraper_count)]
db_connect_and_create()
bad_zip_list, good_zip_list = db_load_zip_lists()
state = 'United States'
zip_code_list = states_dict[state]
login_threads = []
for scraper in scraper_list:
    thread = Thread(target=scraper.login)
    login_threads.append(thread)
    thread.start()
for thread in login_threads:
    thread.join()
zip_list = list(set(zip_code_list) - set(good_zip_list) - set(bad_zip_list))    
zip_list = grouper(scraper_count, zip_list)
try:
    for zip_tuple in zip_list:
        thread_list = []
        start = time.time()
        for zip_code, scraper in zip(zip_tuple, scraper_list):
            thread = Thread(target=scrape_zip, args=[scraper, zip_code])
            thread_list.append(thread)
            thread.start()
        for thread in thread_list:
            thread.join()
        for zip_code, scraper in zip(zip_tuple, scraper_list):
            get_region_id(scraper, zip_code)
        end = time.time()
        print(end-start)
finally:
    for scraper in scraper_list:
        scraper.driver.quit()