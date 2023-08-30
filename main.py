from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import time
import os
import selenium.webdriver.support.expected_conditions as ec
import pandas as pd
from zip_codes import states_dict

#TODO Use args to determine what states, or all
#TODO Add log to log ending zip when crash

#loads or creates bad_zipcode file into dataframe
def bad_zips_load():
    bad_zips_path = 'bad_zipcodes.csv'
    try:
        bad_zips_df = pd.read_csv(bad_zips_path)
    except FileNotFoundError:
        bad_zips_df = pd.DataFrame({'Zip Codes' : []})
        bad_zips_df.to_csv(bad_zips_path, index=False)
    return bad_zips_df

#loads zipcode url on loop in case of connection loss or timeout
def load_zip_url():
    while True:
        try:
            driver.get(f'https://www.redfin.com/zipcode/{zip_code}/filter/include=sold-1yr')
            break
        except TimeoutException:
            time.sleep(5)
            pass

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
    
state = 'Iowa'
options = set_options()
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=10)

url = 'https://www.redfin.com/login'
driver.get(url)


bad_zips_df = bad_zips_load()
zip_code_list = states_dict[state]
login()
bad_zip_list = bad_zips_df['Zip Codes'].to_list()

for zip_code in zip_code_list: #zip_code_list:
    #TODO Better logging
    #try:
    if zip_code not in bad_zip_list:
        load_zip_url()

        #checks if zip code url is bad, adds to bad zip codes
        if driver.current_url == 'https://www.redfin.com/sitemap' or driver.current_url == 'https://www.redfin.com/404':
            bad_zips_df.loc[len(bad_zips_df.index)] = {'Zip Codes' : zip_code}
            bad_zips_df.to_csv(bad_zips_path, index=False)
        
        #makes sure there is a home sold before downloading
        else:
            wait.until(ec.invisibility_of_element(['css selector', '.cell']))
            home_number = (driver.find_element('css selector', '.homes'))
            home_number = int(home_number.text.split()[0].replace(',',""))
            if home_number > 0:
                wait.until(ec.invisibility_of_element(['css selector', '.progress-bar']))
                download_csv()
    '''
    except Exception:
        print(zip_code)
        break
    '''
        
        
