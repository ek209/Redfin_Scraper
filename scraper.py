import selenium.webdriver.support.expected_conditions as ec
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import os
import datetime
import time

class Scraper():
    def __init__(self):
        self.driver, self.wait = self.init_driver_wait()

    #inits driver and wait object for scraping
    def init_driver_wait(self):
        options = self.set_options()
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, timeout=10)
        return driver, wait

    #sets options for scraping data
    def set_options(self):
        download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH') + f'\\{datetime.date.today()}\\'
        options = Options()
        options.add_argument('-headless')
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", download_path)
        return options
    
    #waits for element to load and clicks, if keys are passed sends keys
    def wait_and_click(self, css_selector, keys=None):
        driver, wait = self.driver, self.wait
        wait.until(ec.all_of(ec.presence_of_element_located(['css selector', css_selector])))
        element = driver.find_element('css selector', css_selector)
        element.click()
        if keys != None:
            element.send_keys(keys)

    #method for login page
    def login(self):
        url = 'https://www.redfin.com/login'
        self.driver.get(url)
        time.sleep(2)
        rf_email = os.environ.get('REDFIN_EMAIL')
        rf_password = os.environ.get('REDFIN_PASSWORD')
        self.wait_and_click('input.text', rf_email)
        self.wait_and_click('.password', rf_password)

        #signin button
        self.wait_and_click('button.button:nth-child(5)')
        time.sleep(2)
    
    #clicks excel download button
    def download_csv(self):
        self.wait_and_click("#download-and-save")
