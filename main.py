from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import os

download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH')
options = Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", "C:\\Users\\fresh\\Desktop\\Erik\ Python\\Porfolio_Projects\\Redfin_Scraper_Selenium\\csv_folder")
driver = webdriver.Firefox(options=options)

url = 'https://www.redfin.com/'
zip_code = 53012
driver.get(url)
time.sleep(2)
search_bar = driver.find_element('css selector', '#search-box-input')
search_bar.click()
search_bar.send_keys(zip_code)

send_search_button = driver.find_element('css selector', '#tabContentId0 > div > div > form > div.search-container.inline-block > button')
send_search_button.click()
time.sleep(5)
google_iframe = driver.find_element('css selector', "#credential_picker_container > iframe:nth-child(1)")
driver.switch_to.frame(google_iframe)
google_close_button = driver.find_element('css selector', '#close')
google_close_button.click()
driver.switch_to.default_content()

time.sleep(1)
table_button = driver.find_element('css selector', '.displayModeToggler > button:nth-child(2)')
table_button.click()

for_sale = driver.find_element('css selector', 'div.CustomFilter:nth-child(1) > div:nth-child(1)')
for_sale.click()

show_more = driver.find_element('css selector', '#solds-expandable-segment > div:nth-child(2) > div:nth-child(1)')
show_more.click()

download_csv_button = driver.find_element('css selector', "html body.customer-facing.customer-ui.route-SearchPage.tableMode div#content div div#right-container.map.collapsedList div#results-display div div.HomeViews div.DownloadAndSave div.viewingPage a#download-and-save.downloadLink")
download_csv_button.click()
