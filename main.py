from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import time
import os
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as ec
import pandas as pd
from zip_codes import states_dict

#TODO Use args to determine what states, or all
#TODO Add log to log ending zip when crash
#TODO More consistent login page handling.
#TODO More consistent waits.
#TODO Fix occasional double download (This may be issue with multiple zip codes on )

#waits for element to load and clicks, if keys are passed sends keys
def wait_and_click(css_selector, keys=None):
    wait.until(ec.all_of(ec.presence_of_element_located(['css selector', css_selector])))
    element = driver.find_element('css selector', css_selector)
    element.click()
    if keys != None:
        element.send_keys(keys)

#trys to click to close tag from table page search bar
def close_tags(css_selector):
    
    try:
        driver.find_element('css selector',  css_selector).click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
        pass

def download_csv():
    #download
    wait_and_click("#download-and-save")

def login():
    rf_email = os.environ.get('REDFIN_EMAIL')
    rf_password = os.environ.get('REDFIN_PASSWORD')
    time.sleep(3)

    #google container
    wait_and_click('#credential_picker_container > iframe:nth-child(1)')
    iframe = driver.find_element('css selector', '#credential_picker_container > iframe:nth-child(1)')
    driver.switch_to.frame(iframe)
    time.sleep(.2)
    
    #google close
    wait_and_click('#close')
    driver.switch_to.default_content()

    #close qr box popup
    try:
        wait_and_click('.closeIcon')
    except (NoSuchElementException, TimeoutException):
        pass

    #login button
    wait_and_click('.margin-horiz-medium > button:nth-child(1)')
    
    #enters email
    wait_and_click('span.input:nth-child(1) > div:nth-child(1) > input:nth-child(1)', rf_email)

    #clicks continue button
    wait_and_click('.submitButton')

    #enters password
    wait_and_click('.password', rf_password)
    
    #submits password
    wait_and_click('.submitButton')
    time.sleep(2)
    
state = 'Iowa'
download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH') + f'\\{datetime.date.today()}\\{state}'
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", download_path)
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=10)

url = 'https://www.redfin.com/'
driver.get(url)

#bad_zips_df = pd.DataFrame({'Zip Codes' : []})
#bad_zips_df.to_csv('bad_zipcodes.csv', index=False)
bad_zips_df = pd.read_csv('bad_zipcodes.csv')

zip_code_list = states_dict[state]
login()
bad_zip_list = bad_zips_df['Zip Codes'].to_list()

for zip_code in zip_code_list: #zip_code_list:
    #TODO Better logging
    #try:
    if zip_code not in bad_zip_list:
        
        driver.get(f'https://www.redfin.com/zipcode/{zip_code}/filter/include=sold-1yr')
        
        #checks if zip code url is bad, adds to bad zip codes
        if driver.current_url == 'https://www.redfin.com/sitemap' or driver.current_url == 'https://www.redfin.com/404':
            bad_zips_df.loc[len(bad_zips_df.index)] = {'Zip Codes' : zip_code}
            bad_zips_df.to_csv('bad_zipcodes.csv', index=False)
        
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
        
        
