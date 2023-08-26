from selenium import webdriver
import time

url = 'https://www.redfin.com/'
zip_code = 53012
driver = webdriver.Firefox()
driver.get(url)
time.sleep(2)
search_bar = driver.find_element('css selector', '#search-box-input')
search_bar.click()
search_bar.send_keys(zip_code)

send_search_button = driver.find_element('css selector', '#tabContentId0 > div > div > form > div.search-container.inline-block > button')
send_search_button.click()