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


#searches the zip code in the search bar of the table page
def search_zip(zip_code):
    try:
        driver.find_element('css selector','button.Button:nth-child(3)').click()
    except NoSuchElementException:
        pass
    #clears past search tags
    close_tags('.btn-clear-search-input')
    close_tags('.Tag__remove')

    #search bar
    wait_and_click('.search-container')

    #send keys to search bar
    wait_and_click('#search-box-input', f"Zip: '{zip_code}'")
    wait_and_click('#search-box-input', Keys.ENTER)

def first_search():
    first_zip = zip_code_list[0]
    zip_code_list.pop(0)

    #enters first zip into search bar
    wait_and_click('#search-box-input', first_zip)

    #sends search
    wait_and_click('#tabContentId0 > div > div > form > div.search-container.inline-block > button')


def download_csv():
    #download
    wait_and_click("#download-and-save")

def set_search_settings():
    
    time.sleep(5)
    #show table button
    wait_and_click('button.ModeOption:nth-child(2)')

    #for sale button
    wait_and_click('div.CustomFilter:nth-child(1) > div:nth-child(1)')

    #expand
    wait_and_click('#solds-expandable-segment > div:nth-child(2) > div:nth-child(1)')

    #sold
    time.sleep(3)
    wait_and_click('div.expanded:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > div:nth-child(1) > label:nth-child(1) > input:nth-child(1)')
    
    # year button
    time.sleep(3)
    wait_and_click('div.padding-left-medium:nth-child(6) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > div:nth-child(1) > label:nth-child(1) > input:nth-child(1)')

    #collapse
    wait_and_click('div.expanded:nth-child(2) > div:nth-child(1)')

    #done button
    wait_and_click('button.primary:nth-child(2)')

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

##TODO attempt to bypass first_search by going directly to filtered url
zip_code_list = states_dict[state]
login()
#first_search()
#set_search_settings()
#download_csv()
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
        
        
