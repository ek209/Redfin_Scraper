from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import time
import os
from selenium.webdriver.common.keys import Keys
#TODO Handle bad zip codes
#TODO Handle waits better (use implicit waits)

def search_zip(zip_code):
    try:
        time.sleep(1)
        tag_remove = driver.find_element('css selector', '.Tag__remove')
        tag_remove.click()
    except NoSuchElementException:
        pass

    small_search_bar = driver.find_element('css selector', '.search-container')
    small_search_bar.click()

    small_input = driver.find_element('css selector', '#search-box-input')
    small_input.send_keys(f"Zip: '{zip_code}'")
    small_input.send_keys(Keys.ENTER)

    #small_search_send = driver.find_element('css selector', 'button.inline-block')
    #small_search_send.click()
    time.sleep(5)

def first_search():
    first_zip = united_states_zip_code_list[0]
    united_states_zip_code_list.pop(0)

    search_bar = driver.find_element('css selector', '#search-box-input')
    search_bar.click()
    search_bar.send_keys(first_zip)

    send_search_button = driver.find_element('css selector', '#tabContentId0 > div > div > form > div.search-container.inline-block > button')
    send_search_button.click()
    time.sleep(5)

def download_csv():
    table_button = driver.find_element('css selector', '.displayModeToggler > button:nth-child(2)')
    table_button.click()

    download_csv_button = driver.find_element('css selector', "html body.customer-facing.customer-ui.route-SearchPage.tableMode div#content div div#right-container.map.collapsedList div#results-display div div.HomeViews div.DownloadAndSave div.viewingPage a#download-and-save.downloadLink")
    download_csv_button.click()

def set_search_settings():

    table_button = driver.find_element('css selector', '.displayModeToggler > button:nth-child(2)')
    table_button.click()

    for_sale = driver.find_element('css selector', 'div.CustomFilter:nth-child(1) > div:nth-child(1)')
    for_sale.click()
    time.sleep(3)

    show_more = driver.find_element('css selector', '#solds-expandable-segment > div:nth-child(2) > div:nth-child(1)')
    show_more.click()
    time.sleep(3)

    sold_radio_button = driver.find_element('css selector', 'div.expanded:nth-child(1) > div:nth-child(1) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > div:nth-child(1) > label:nth-child(1) > input:nth-child(1)')
    sold_radio_button.click()
    time.sleep(3)

    one_year_radio = driver.find_element('css selector', 'div.padding-left-medium:nth-child(6) > span:nth-child(1) > span:nth-child(1) > div:nth-child(1) > div:nth-child(1) > label:nth-child(1) > input:nth-child(1)')
    one_year_radio.click()
    time.sleep(3)

    close_expansion = driver.find_element('css selector', 'div.expanded:nth-child(2) > div:nth-child(1)')
    close_expansion.click()
    time.sleep(1)

    done_button = driver.find_element('css selector', 'button.primary:nth-child(2)')
    done_button.click()

def login():
    rf_email = os.environ.get('REDFIN_EMAIL')
    rf_password = os.environ.get('REDFIN_PASSWORD')
    login_button = driver.find_element('css selector', '.margin-horiz-medium > button:nth-child(1)')
    login_button.click()
    time.sleep(1)

    login_field = driver.find_element('css selector', 'span.input:nth-child(1) > div:nth-child(1) > input:nth-child(1)')
    login_field.send_keys(rf_email)

    continue_button = driver.find_element('css selector', '.submitButton')
    continue_button.click()
    time.sleep(2)

    password_field = driver.find_element('css selector', '.password')
    password_field.send_keys(rf_password)

    cont_button = driver.find_element('css selector', '.submitButton')
    cont_button.click()
    time.sleep(1)

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

url = 'https://www.redfin.com/'
driver.get(url)
time.sleep(4)

login()
first_search()
set_search_settings()

for zip_code in united_states_zip_code_list:
    if zip_code not in []:
        try:
            driver.find_element('css selector', '.guts')
            driver.find_element('css selector', 'button.Button:nth-child(3)').click()
        except NoSuchElementException:
            home_number = (driver.find_element('css selector', '.homes'))
            home_number = int(home_number.text.split()[0])
            if home_number > 0:    
                download_csv()

        search_zip(zip_code)
