from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import time
import os
import selenium.webdriver.support.expected_conditions as ec
import pandas as pd
from zip_codes import states_dict, bad_zips_load

#TODO Use args to determine what states, or all
#TODO Add log to log ending zip when crash
#TODO In process major revamp
#TODO Collect region ids and market in link directly to api download

def init_driver_wait():
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, timeout=10)
    return driver, wait

#waits for element to load and clicks, if keys are passed sends keys
def wait_and_click(css_selector, keys=None):
    wait.until(ec.all_of(ec.presence_of_element_located(['css selector', css_selector])))
    element = driver.find_element('css selector', css_selector)
    element.click()
    if keys != None:
        element.send_keys(keys)


#clicks excel download button
def download_csv():
    wait_and_click("#download-and-save")

    
#method for login page
def login():
    url = 'https://www.redfin.com/login'
    driver.get(url)
    time.sleep(2)
    rf_email = os.environ.get('REDFIN_EMAIL')
    rf_password = os.environ.get('REDFIN_PASSWORD')
    wait_and_click('input.text', rf_email)
    wait_and_click('.password', rf_password)

    #signin button
    wait_and_click('button.button:nth-child(5)')
    
    time.sleep(2)

def set_options():
    download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH') + f'\\{datetime.date.today()}\\{state}'
    options = Options()
    options.add_argument('-headless')
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", download_path)
    return options
    
state = 'United States'
bad_zips_path = 'bad_zipcodes.csv'
bad_zips_df, bad_zip_list = bad_zips_load(bad_zips_path)
zip_code_list = states_dict[state]
try:
    region_data = pd.read_csv('region_data.csv')
except FileNotFoundError:
    region_data = pd.DataFrame({'Region ID' : [],
                                'Market' : [],
                                'Region Type ID' : [],
                                'RF Search Value' : []})
    region_data.to_csv('region_data.csv', index=False)

options = set_options()
driver, wait = init_driver_wait()
login()
good_zip_list = region_data['RF Search Value'].to_list()
print(good_zip_list)
for zip_code in zip_code_list:    
    #TODO Better logging
    #try:
    if zip_code not in bad_zip_list and zip_code not in good_zip_list:
        while True:
            try:
                driver.get(f'https://www.redfin.com/zipcode/{zip_code}/filter/include=sold-5yr')
                #driver.get(f'https://www.redfin.com/stingray/api/gis-csv?al=2&has_deal=false&has_dishwasher=false&has_laundry_facility=false&has_laundry_hookups=false&has_parking=false&has_pool=false&has_short_term_lease=false&include_pending_homes=false&isRentals=false&is_furnished=false&market={state.lower()}num_homes=35000&ord=redfin-recommended-asc&page_number=1&region_id=22614&region_type=2&sold_within_days=1825&status=9&travel_with_traffic=false&travel_within_region=false&uipt=1,2,3,4,5,6,7,8&utilities_included=false&v=8')
                time.sleep(2)

                #checks if zip code url is bad, adds to bad zip codes
                if driver.current_url == 'https://www.redfin.com/sitemap' or driver.current_url == 'https://www.redfin.com/404':
                    bad_zips_df.loc[len(bad_zips_df.index)] = {'Zip Codes' : zip_code}
                    bad_zips_df.to_csv(bad_zips_path, index=False)
                    break
                
                #makes sure there is a home sold before downloading
                else:
                    wait.until(ec.invisibility_of_element(['css selector', '.cell']))
                    wait.until(ec.invisibility_of_element(['css selector', '.progress-bar']))
                    dict = driver.execute_script('return dataLayerInitializationValues')
                    market = driver.execute_script('return searchMarket')
                    df_dict = { "Region ID" : dict['region_id'],
                                'Market' : market,
                                'Region Type ID' : dict['region_type_id'],
                                'RF Search Value' : zip_code}
                    region_data.loc[len(region_data.index)] = df_dict
                    region_data.to_csv('region_data.csv', index=False)
                    break
            except TimeoutException:
                pass
                

'''
    except Exception:
        print(zip_code)
        break
    '''
        
        
