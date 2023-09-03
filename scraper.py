import selenium.webdriver.support.expected_conditions as ec
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import os
import datetime
import time

class Scraper():
    """Scraper object to scrape webpages for data, specifically REDFIN
    """
    def __init__(self):
        """Initialization Scraper's driver and wait objects.
        """
        self.driver, self.wait = self.init_driver_wait()

    def init_driver_wait(self):
        """Initializes driver and wait object and set_options func to set driver
        options.

        Returns:
            driver, wait: Returns driver and wait for Scraper class
        """
        options = self.set_options()
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, timeout=10)
        return driver, wait

    def set_options(self):
        """Sets options for driver object for Scraper

        Returns:
            Options:  returns an options objects to load into driver
        """
        download_path = os.environ.get('REDFIN_CSV_DOWNLOAD_PATH') + f'\\{datetime.date.today()}\\'
        options = Options()
        options.add_argument('-headless')
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", download_path)
        return options
    
    def wait_and_click(self, css_selector, keys=None):
        """Waits for web element to load and then clicks, if keys are sent, sends
        keys to web element.

        Args:
            css_selector (String): Css selector to identify object to click and send keys
            keys (_type_, optional): Keys to send to web element. Defaults to None.
        """
        driver, wait = self.driver, self.wait
        wait.until(ec.all_of(ec.presence_of_element_located(['css selector', css_selector])))
        element = driver.find_element('css selector', css_selector)
        element.click()
        if keys != None:
            element.send_keys(keys)

    def login(self):
        """Logs the Scraper into the website for scraping.
        """
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
    
    def download_csv(self):
        """Downloads the csv from  redfin webpage.
        """
        self.wait_and_click("#download-and-save")
