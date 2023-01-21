from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService


class RakutenBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ 楽天ウェブサーチにログイン(via Infoseek) """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        #
        # 楽天ログイン ～ sso対応のinfoseek経由で
        driver.get("https://www.infoseek.co.jp/")
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログイン")
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        ####
        logger.debug('  wait for (By.LINK_TEXT,u"ログイン")')
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, u"ログイン")))
        driver.find_element_by_link_text(u"ログイン").click()
        #
        po = (By.ID, "scrollingLayer")
        logger.debug(f'  wait for {po}; ログイン画面')
        wait.until(EC.visibility_of_element_located(po))
        po = (By.CSS_SELECTOR, "#user_id")
        logger.debug(f'  wait for {po}; ユーザ入力')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['id'])
        po = (By.CSS_SELECTOR, "#cta > div")
        logger.debug(f'  wait for {po}; 次へ')
        # wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).click()
        # ----
        po = (By.CSS_SELECTOR, "#password_current")
        logger.debug(f'  wait for {po}; PW入力')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['pw'])
        driver.find_element(*po).send_keys(Keys.ENTER)
        ###
        po = (By.LINK_TEXT, "ログアウト")
        logger.debug(f'  wait for {po}')
        wait.until( EC.visibility_of_element_located(po))
        #
        return self.is_element_present(*po)

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### Logout
        driver.get("https://www.infoseek.co.jp/logout")
        #
        return True
