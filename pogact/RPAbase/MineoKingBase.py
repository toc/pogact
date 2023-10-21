from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import RPAbase.RPAUserService


class MineoKingBase(RPAbase.RPAUserService.RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ マイネ王にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://king.mineo.jp/login")
        pageobj = (By.ID, 'session_login')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.ID, 'session_password')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])
        #
        pageobj = (By.CSS_SELECTOR, '#new_session > div:nth-child(8) > button')
        driver.find_element(*pageobj).click()
        ###
        pageobj = (By.LINK_TEXT, 'マイページ')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        return self.is_element_present(By.LINK_TEXT, u"マイページ")


    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait
        #
        logger.info( f'  マイネ王からログアウト')
        # ==============================
        driver.get("https://king.mineo.jp/my")
        # ------------------------------
        logger.debug(f'  - ボタン押下: ログアウト')
        pageobj = (By.LINK_TEXT,'ログアウト')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        driver.find_element(*pageobj).click()
        #
        logger.debug(f'ログアウト確認')
        # ==============================
        wk = ''
        if self.is_alert_present():
            wk = self.close_alert_and_get_its_text()
            logger.debug(f'  Alert TEXT: <{wk}>')
        result = True if re.match('.*ログアウトしますか？$', wk) else False
        logger.debug(f'  [{result}]: >{wk.split()[0]}<')
        #
        return result

