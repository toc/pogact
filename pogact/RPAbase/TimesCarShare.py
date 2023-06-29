#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import RPAbase.RPAbase


class TimesCarShare(RPAbase.RPAbase.RPAbase):
    """
    """
    def pilot_login(self, account):
        """ Times Car Share にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://share.timescar.jp/")
        logger.debug('  wait for (By.CLASS_NAME, r"header")')
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, r'header')))
        result = self.is_element_present(By.ID, r'tpLogin')
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        logger.debug('  wait for (By.ID, r"linkButton")')
        wait.until(EC.element_to_be_clickable((By.ID, r'tpLogin')))

        driver.find_element(By.ID,"cardNo1").clear()
        driver.find_element(By.ID,"cardNo1").send_keys(account['id1'])
        driver.find_element(By.ID,"cardNo2").clear()
        driver.find_element(By.ID,"cardNo2").send_keys(account['id2'])
        driver.find_element(By.ID,"tpPassword").clear()
        driver.find_element(By.ID,"tpPassword").send_keys(account['pw'])
        driver.find_element(By.ID,"tpLogin").click()
        ###
        logger.debug('  wait for link_text "ログアウト"')
        wait.until(
            EC.visibility_of_element_located(
                (By.LINK_TEXT, r'ログアウト')
            )
        )
        return self.is_element_present(By.LINK_TEXT, u"ログアウト")

    def pilot_logout(self):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### Times Car Shareからのログアウト
        driver.get("https://share.timescar.jp/")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'header')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.LINK_TEXT,u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
