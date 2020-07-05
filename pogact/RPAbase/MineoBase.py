from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import RPAbase.RPAbase


class MineoBase(RPAbase.RPAbase.RPAbase):
    """
    """
    def pilot_login(self, account):
        """ Times Car Share にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://login.eonet.jp/auth/Login/mineo")
        logger.debug('  wait for (By.ID, "header")')
        wait.until(EC.visibility_of_element_located((By.ID, 'header')))

        logger.debug('  wait for visibility_of_element_located((By.ID, "eoID")')
        wait.until(EC.visibility_of_element_located((By.ID, "eoID")))
        elm = driver.find_element_by_id("eoID")
        elm.clear()
        elm.send_keys(account['id'])
        driver.find_element_by_id("btnSubmit").click()

        logger.debug('  wait for visibility_of_element_located((By.ID, "password")')
        wait.until(EC.visibility_of_element_located((By.ID, "password")))
        elm = driver.find_element_by_id("password")
        elm.clear()
        elm.send_keys(account['pw'])
        driver.find_element_by_id("btnSubmit").click()

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

        ### mineo からのログアウト
        driver.get("https://my.mineo.jp/")
        wait.until(EC.visibility_of_element_located((By.ID, 'header')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
