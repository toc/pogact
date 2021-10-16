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
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException
from webdrivermanager import ChromeDriverManager
import yaml
from logutils.logger import Logger
import logutils.mailreporter
import RPAbase.RPAbase

class RPAbaseRecapture(RPAbase.RPAbase.RPAbase):
    """
    """

    # @return: driver, wait
    def pilot_setup(self, options=None, username=None, waitsec=10):
        """
        Called from pilot().
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        logger = self.logger
        wk = self.config.get('general', {})  
        userdata_dir = wk.get('userdatadir',r'C:\Users\Default\AppData\Local\Google\Chrome\User Data')  
        if username is None:
            raise NotImplementedError('pilot_setup() with username.')

        options.add_argument(f'--user-data-dir={userdata_dir}\profile_{username}')

        return super().pilot_setup(options,waitsec)
   
