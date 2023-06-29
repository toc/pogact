#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RPAUserService import RPAUserService
import time

class SBISec(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ SBI証券にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info("  Try to login SBI証券")
        driver.get("https://site1.sbisec.co.jp/ETGate/")
        # time.sleep(1)
        # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.login-link"))).click()
        wait.until(EC.visibility_of_element_located((By.ID, r'link02')))
        driver.find_element(By.NAME,"user_id").clear()
        driver.find_element(By.NAME,"user_id").send_keys(account['id'])
        driver.find_element(By.NAME,"user_password").clear()
        driver.find_element(By.NAME,"user_password").send_keys(account['pw'])
        logger.debug("  -- Click SUBMIT.")
        driver.find_element(By.NAME,"ACT_login").click()
        #
        time.sleep(1.5)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))
        #
        return


    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### SBI証券からログアウト
        driver.get("https://site1.sbisec.co.jp/ETGate/")
        wait.until(EC.visibility_of_element_located((By.ID, r'link02')))
        result = self.is_element_present(By.XPATH, r'//*[@id="logoutM"]/a')

        logger.debug(f'  -- XPAHT[//*[@id="logoutM"]/a] exists? {result}')
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.XPATH,r'//*[@id="logoutM"]/a').click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
