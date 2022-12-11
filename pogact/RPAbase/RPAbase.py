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
        self.reporter = None
        self.wait = None
        self.config = {}
        self.pilot_param = {}
        self.pilot_result = []
        # form Katalon++
        self.accept_next_alert = True


    def prepare(self, subject=__name__):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare logger, work file/folder, and so on.
        """
        # today
        now = datetime.datetime.now()
        self.appdict.data['now'] = now
        self.appdict.data['today'] = now.replace(hour=0,minute=0,second=0,microsecond=0)
        self.appdict.data['need_report'] = 0
        # logger
        self.logger = Logger(self.appdict.name, clevel=DEBUG if __debug__ else INFO, flevel=DEBUG)
        logger = self.logger
        # Setting file
        try:
            with open(r'settings.yaml', 'r', encoding=r'utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(self.exception_message(e))
            self.config = {}
        # last done file
        try:
            with open('last_done.yaml', 'r', encoding='utf-8') as f:
                self.last_done = yaml.safe_load(f)
        except Exception as e:
            logger.error(self.exception_message(e))
            self.last_done = {}
        # mail reporter
        try:
            self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', subject)
        except Exception as e:
            self.logger.warn(self.exception_message(e))
            self.reporter = None

    # @return: driver, wait
    def pilot_setup(self, options=None, waitsec=10):
        """
        Called from pilot().
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        logger = self.logger
        msg = ''

        # Ad-hoc workaround for Google Chrome v.93 or later.
        ### See: https://stackoverflow.com/questions/69034343/chromedriver-session-timeouts-in-version-93
        options.add_argument("--disable-gpu")  

        try:
            ld_webdriver = self.last_done.get('WebDriver',{})
            logger.debug(f"  -- last_done.webdriver: {ld_webdriver}")
            previous = ld_webdriver.get('Chrome',['',datetime.datetime.min])
            logger.debug(f"  -- get_download_path() == Re-use driver.")
            driver_path = previous[0]

            logger.debug(f"  driver_path: {driver_path}")
            self.driver = webdriver.Chrome(driver_path, options=options)
        except (SessionNotCreatedException, OSError) as e:
            """
            SessionNotCreatedException:　Chromeのバージョンアップを想定しWebDriverのバージョンアップを試みる。
            OSError: ChromeDriver 未取得の可能性あるため取得を試みる。
            """
            logger.warn(f'  !! {type(e)}: {e.args if hasattr(e,"args") else e}')
            msg += f"Maybe unmatch chromewebdriver, And try to update chrome driver... <{sys._getframe().f_lineno}@{__file__}>"
            logger.warn(f'  !! {msg}')

            try:
                cdm = ChromeDriverManager()
                logger.debug(f"  -- download_and_install() == Try to update driver")
                driver_path = cdm.download_and_install()[0]
                ld_webdriver['Chrome'] = [driver_path,datetime.datetime.now()]
                self.last_done['WebDriver'] = ld_webdriver
                logger.debug(f"  driver_path: {driver_path}")
                self.driver = webdriver.Chrome(driver_path, options=options)
            except Exception as e:
                # msg += f" -- {type(e)}: {e.msg}\n"
                logger.critical(f'  !! Cannot update ChromeDriver.  {self.exception_message(e)}')
                msg += f"\n!! Cannot update ChromeDriver. <{sys._getframe().f_lineno}@{__file__}>.  Exit."
                msg += "\n"
        except WebDriverException as e:
            msg += f" -- {self.exception_message(e)}\n"
            msg += f"!! Cannot instantiate WebDriver<{sys._getframe().f_lineno}@{__file__}>.  Exit.\n"
            msg += "\n"
        except Exception as e:
            msg += f" -- {self.exception_message(e)}\n"
            msg += "\n"
        finally:
            if self.driver is None:
                logger.critical(msg)
                raise SessionNotCreatedException(msg)

        self.driver.implicitly_wait(waitsec)
        logger.debug(f'  -- {self.driver}')
        self.wait = WebDriverWait(self.driver, waitsec)

        return (self.driver, self.wait)
   
    def silent_setup(self, driver, wait, logger):
        self.driver = driver
        self.wait = wait
        self.logger = logger
        logger.debug(f'((silent_setup)): done')


    def pilot_login(self, account):
        """
        Called from pilot().
        Log-in target web site.
        """
        raise NotImplementedError('pilot_login()')
    
    def pilot_logout(self):
        """
        Called from pilot().
        Log-out from web site.
        """
        raise NotImplementedError('pilot_logout()')

    def pilot(self):
        """
        Pilot automatically, to get your informations.
        """
        raise NotImplementedError('pilot()')

    def report(self, msg=None, subject=None, level=INFO):
        if self.reporter is not None:
            if msg is None:
                msg = self.pilot_result
            if subject is not None:
                self.reporter.setSubjectBase(subject)
            self.reporter.report(msg, level)

    def tearDown(self):
        # Save last_done
        try:
            with open('last_done.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(self.last_done, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(self.exception_message(e))
        # Clear webdriver
        if self.driver:
            self.driver.quit()
        self.logger.debug(self.pilot_result)

    def save_current_html(self,substr='wk',suffix='tmp'):
        # save current html
        fname = self.appdict.wkfile(substr,suffix)
        try:
            with open(fname, 'w', encoding=r'utf-8') as f:
                f.write(self.driver.page_source)
        except Exception as e:
            self.logger.error(f'!! Cannot save current page_source')
            self.logger.error(self.exception_message(e))

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to.alert
        except NoAlertPresentException: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def assertEqual(self, a, b):
        if a != b:
            raise AssertionError(f"Unexpected result: >{b}<")
        return True

    def exception_message(self, e):
        return f'Caught Exception: {type(e)} {e.args if hasattr(e,"args") else str(e)}'
