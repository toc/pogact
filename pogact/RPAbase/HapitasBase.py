import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService


class HapitasBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ Hapitas にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://hapitas.jp/auth/signin/")
        pageobj = (By.ID, 'global-navigation')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        # if self.is_element_present(By.ID, 'PRmodal'):
        #     logger.warn('  PRmodal 発見。閉じます。')
        #     driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"会員ログイン")
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()

        pageobj = (By.ID, 'email_main')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.element_to_be_clickable(pageobj))
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.ID, 'password_main')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])

        driver.find_element(By.CSS_SELECTOR,".btn_login_main_white").click()
        logger.debug('  SUBMIT login.')
        ###
        if self.is_element_present(By.CSS_SELECTOR, '.top_modal'):
            logger.warn('  top_modal 発見。閉じます。')
            driver.find_element(By.CSS_SELECTOR, '.top_modal_close_btn').click()
        # logger.debug('  wait for id "dropdown-menu"')
        # wait.until(
        #     EC.visibility_of_element_located((By.ID, 'dropdown-menu'))
        # )
        # return self.is_element_present(By.ID, 'openswitch')
        return self.is_element_present(By.LINK_TEXT, 'メニュー')


    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.debug('  Try to log out.  Visit logout URL directly.')
        driver.get("https://hapitas.jp/auth/logout/")

        pageobj = (By.ID, 'global-navigation')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        for i in range(6):
            result = self.is_element_present(By.LINK_TEXT, u"会員ログイン")
            if result == True:
                break
            time.sleep(0.5)
        logger.debug(f'  -- 「会員ログイン」の存在確認: Trueでlogout済み→[{result}]')

        return result
