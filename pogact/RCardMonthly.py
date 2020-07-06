# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import logutils.AppDict
import time
import re
import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import yaml
from RPAbase.RCardBase import RCardBase
from logutils.AppDict import AppDict


class RCardMonthly(RCardBase):
    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'RCardMonthly', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        super().prepare(self.appdict.name)
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return super(RCardMonthly, self).pilot_setup(options)

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(f'  @@pilot_internal: START')

        title, pay_by, status, bill = ('','','','')
        bills = []
        try:
            # Wait page top
            logger.debug(f'wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.ghead.rce-ghead > div.service-bar")))')
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.ghead.rce-ghead > div.service-bar")))

            # get　invoice summary
            card_info = driver.find_element_by_css_selector("#top > div.rce-l-wrap.is-grey.rce-main > div > div.rce-billInfo.rf-card.rf-card-square.rf-card-edge > div.rce-contents")
            summary = card_info.find_element_by_css_selector("div.rce-columns > div.rce-columns-cell.rce-billInfo-month")
            bills.append(summary.find_element_by_css_selector("h3.rf-title-collar.rce-title-belt-first").text)
            bills.append(summary.find_element_by_css_selector("table:nth-child(2) > tbody > tr:nth-child(1) > td").text)
            bills.append(summary.find_element_by_css_selector("#parent-balance > div.rf-label.rce-annotation-pc-top.rce-annotation--blue").text)
            bills.append(summary.find_element_by_css_selector("#js-bill-mask > em").text)
        except Exception as e:
            bills.append(f'Caught Exception: {type(e)} {e.args if hasattr(e,args) else str(e)}')
        finally:
            self.pilot_result.append( [account.get("name","Unknown"), bills] )

        logger.debug(f'  @@pilot_internal: END')


if __name__ == "__main__":
    try:
        App = RCardMonthly()
        App.prepare()
        App.pilot()
        App.report(
            pprint.pformat(App.pilot_result, width=72)
        )
        App.tearDown()
    except Exception as e:
        print(f'Caught Exception: {type(e)} {e.args if hasattr(e,args) else str(e)}')
        if App.driver is not None:
            App.driver.quit()
