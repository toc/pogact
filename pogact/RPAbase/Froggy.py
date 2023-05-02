from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService
import time

class Froggy(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ SMBC日興 Floggy にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info("  Try to login to 日興Floggy")
        driver.get("https://froggy.smbcnikko.co.jp/ ")
        po = (By.CSS_SELECTOR,'#__layout > div > header > div')
        logger.debug(f"  wait for {po}")
        wait.until(EC.visibility_of_element_located(po))
        po=(By.PARTIAL_LINK_TEXT,'ログイン')
        if self.is_element_present(*po) is not True:
            self.pilot_logout(account)
        #
        driver.find_element(*po).click()
        #
        po = (By.ID, 'js-first-focus')
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['id'])
        po = (By.ID, 'login-form-password')
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['pw'])
        logger.debug("  -- Click SUBMIT.")
        po = (By.XPATH,"//input[@value='ログインする']")
        # po = (By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > div > div > form > div.align-center > input")
        driver.find_element(*po).click()

        # po = (By.CSS_SELECTOR,'#__layout > div > header > div')
        po = (By.LINK_TEXT,'マイ資産')
        logger.debug(f"  wait for {po}")
        wait.until(EC.visibility_of_element_located(po))
        return

    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.info("  Try to logout from 日興Floggy")
        driver.get("https://froggy.smbcnikko.co.jp/myasset")
        po = (By.CSS_SELECTOR,'#__layout > div > header > div')
        logger.debug(f"  wait for {po}")
        wait.until(EC.visibility_of_element_located(po))

        po = (By.LINK_TEXT,'マイ資産')
        result = self.is_element_present(*po)
        if result is True:
            driver.find_element(*po).click()
            po = (By.LINK_TEXT,'ログアウト')
            logger.debug(f"  wait for {po}")
            wait.until(EC.visibility_of_element_located(po))
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(*po).click()
        else:
            logger.info("  It seems to already be logged-out.  Do nothing.")

        return result
