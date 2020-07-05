import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import RPAbase.RPAbase


class CyberhomeBase(RPAbase.RPAbase.RPAbase):
    """
    """
    def pilot_login(self, account):
        """ Cyberhome mailページにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info(f"Try to login to FNJ(cyberhome).")
        # ==============================
        driver.get("https://wmail.cyberhome.ne.jp/login/")
        logger.debug('  wait for (By.ID, u"username")')
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        u = driver.find_element_by_id("username")
        u.clear()
        u.send_keys(account['id'])
        p = driver.find_element_by_id('password')
        p.clear()
        p.send_keys(account['pw'])

        logger.debug('  SUBMIT login.')
        driver.find_element_by_xpath(u"//img[@alt='ログイン']").click()
        time.sleep(5)
        
        return self.is_element_present(By.LINK_TEXT, u"新着をチェック")

    def pilot_logout(self):
        """
        Log-out from web site.
        """
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.info(f"Try to logout from FNJ(zeny).")
        # ==============================
        driver.get('https://wmail.cyberhome.ne.jp/logout/')
