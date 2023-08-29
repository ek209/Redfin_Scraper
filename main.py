from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
import os
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.expected_conditions as ec

#TODO Handle bad zip codes
#TODO Handle waits better (use implicit waits)

#waits for element to load and clicks
def wait_and_click(css_selector, keys=None):
    wait.until(ec.all_of(ec.presence_of_element_located(['css selector', css_selector])))
    element = driver.find_element('css selector', css_selector)
    element.click()
    if keys != None:
        element.send_keys(keys)

def search_zip(zip_code):
    
    #try statements clear last tag if exists
    try:
        driver.find_element('css selector', '.btn-clear-search-input').click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
        pass
    
    try:
        driver.find_element('css selector', '.Tag__remove').click()
    except (NoSuchElementException, TimeoutException):
        pass

    #search bar
    wait_and_click('.search-container')

    #send keys to search bar
    wait_and_click('#search-box-input', f"Zip: '{zip_code}'")
    wait_and_click('#search-box-input', Keys.ENTER)

    #small_search_send = driver.find_element('css selector', 'button.inline-block')
    #small_search_send.click()
    #time.sleep(5)

def first_search():
    first_zip = united_states_zip_code_list[0]
    united_states_zip_code_list.pop(0)

    #enters first zip into search bar
    wait_and_click('#search-box-input', first_zip)

    #sends search
    wait_and_click('#tabContentId0 > div > div > form > div.search-container.inline-block > button')


def download_csv():
    #table
    wait_and_click('.displayModeToggler > button:nth-child(2)')

    #download
    wait_and_click("html body.customer-facing.customer-ui.route-SearchPage.tableMode div#content div div#right-container.map.collapsedList div#results-display div div.HomeViews div.DownloadAndSave div.viewingPage a#download-and-save.downloadLink")

def set_search_settings():
    
    time.sleep(5)
    #show table button
    wait_and_click('button.ModeOption:nth-child(2)')

    #for sale button
    wait_and_click('div.CustomFilter:nth-child(1) > div:nth-child(1)')
    #time.sleep(3)

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
    



states_dict = { 'Alaska' : [num for num in range(99501,99950)],
               'Alabama' : [num for num in range(35004, 36926)]}

united_states_zip_code_list = []
for zip_codes_list in states_dict.values():
    united_states_zip_code_list += zip_codes_list

download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH')
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", download_path)
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, timeout=10)

url = 'https://www.redfin.com/'
driver.get(url)
#time.sleep(4)

login()
first_search()
set_search_settings()
list = []
for zip_code in united_states_zip_code_list:
    if zip_code not in []:
        try:
            time.sleep(1)
            driver.find_element('css selector', '.guts')
            if driver.find_element('css selector', '.header > h3:nth-child(2)').text.split()[0] == 'Sorry,':
                print(zip_code)
            wait_and_click('button.Button:nth-child(3)')
        except NoSuchElementException:
            home_number = (driver.find_element('css selector', '.homes'))
            home_number = int(home_number.text.split()[0].replace(',',""))
            if home_number > 0:
                time.sleep(3)    
                download_csv()

        search_zip(zip_code)
        wait.until(ec.invisibility_of_element(['css selector', '.progress-bar']))
        
