#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import re
from logging import DEBUG, INFO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from webdrivermanager import ChromeDriverManager
import yaml
from logutils.logger import Logger


class RPAbase():
    """
    """

    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        self.driver = None
        self.driverinfo = []
        self.logger = None
        self.wait = None
        self.config = {}
        self.pilot_param = {}
        self.pilot_result = []
        # form Katalon++
        self.accept_next_alert = True


    def prepare(self, name=__name__):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare logger, work file/folder, and so on.
        """
        # logger
        self.logger = Logger(name, clevel=DEBUG if __debug__ else INFO, flevel=DEBUG)
        logger = self.logger
        # Setting file
        try:
            with open(r'settings.yaml', 'r', encoding=r'utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Read settings.yaml: {type(e)} {e.args}')
            self.config = {}
        # last done file
        try:
            with open('last_done.yaml', 'r', encoding='utf-8') as f:
                self.last_done = yaml.safe_load(f)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Read last_done.yaml: {type(e)} {e.args}')
            self.last_done = {}
        # WebDriver update - 1 time per hour (at most)
        try:
            wdinfo = self.last_done.get('WebDriver', {})
            previous_update = wdinfo.get('last_update', datetime.datetime.min)
            update_interval = wdinfo.get('update_interval_by_hour', 6)
            now_minus_1h = datetime.datetime.now() - datetime.timedelta(hours=update_interval)
            if previous_update < now_minus_1h:
                dm = ChromeDriverManager()
                self.driverinfo = dm.download_and_install()
                wdinfo['last_update'] = datetime.datetime.now()
                wdinfo['driver_info'] = list(self.driverinfo)
            else:
                self.driverinfo = wdinfo.get('driver_info', [])
        except Exception as e:
            logger.error(f' Caught Ex(Raise upstream): During manage webdriver: {type(e)} {e.args}')
            self.driverinfo = []
            raise(e)

    # @return: driver, wait
    def pilot_setup(self, options=None):
        """
        Called from pilot().
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        # ブラウザーを起動
        self.driver = webdriver.Chrome(self.driverinfo[1], options=options)
        # self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver,10)

        return (self.driver, self.wait)
   
    def pilot_login(self, account):
        """
        Called from pilot().
        Log-in target web site.
        """
        driver = self.driver

        driver.get("https://zeny.cyberhome.ne.jp/user/login.aspx")
        driver.find_element_by_id("LoginBody1_Tb_Account").click()
        driver.find_element_by_id("LoginBody1_Tb_Account").send_keys(account['id'])
        driver.find_element_by_id("LoginBody1_Tb_Passsword").click()
        driver.find_element_by_id("LoginBody1_Tb_Passsword").send_keys(account['pw'])
        driver.find_element_by_id("LoginBody1_Btn_Login").click()
        # pass
    
    def pilot_logout(self):
        """
        Called from pilot().
        Log-out from web site.
        """
        # pass
        driver = self.driver

        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='田中俊明'])[1]/following::img[1]").click()

    def pilot(self):
        """
        Pilot automatically, to get your informations.
        """
        raise(NotImplementedError)


    def tearDown(self):
        # Save last_done
        try:
            with open('last_done.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.last_done, f)
        except Exception as e:
            self.logger.error(f' Caught Ex(Ignore): Save last_done.yaml: {type(e)} {e.args}')
        # Clear webdriver
        if self.driver:
            self.driver.quit()
        self.logger.debug(self.pilot_result)

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def assertEqual(self, a, b):
        if a == b:
            pass
        else:
            raise AssertionError(f"Unexpected result: >{b}<")
