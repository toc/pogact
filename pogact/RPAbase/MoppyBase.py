import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService


class MoppyBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ モッピー(Moppy)にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://ssl.pc.moppy.jp/login/")
        pageobj = (By.ID, 'global-menu')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログイン")
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()

        pageobj = (By.NAME, 'mail')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.element_to_be_clickable(pageobj))
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.NAME, 'pass')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])
        #
        time.sleep(2)        # Moppy may need some preparation.
        #
        driver.find_element(By.CSS_SELECTOR,".a-btn__login").click()
        logger.debug('  SUBMIT login.')
        ###
        pageobj = (By.TAG_NAME, 'body')
        wait.until(EC.visibility_of_element_located(pageobj))
        if self.is_element_present(By.ID, 'modalTop'):
            logger.warn('  modalTop 発見。閉じます。')
            driver.find_element(By.ID, 'modalTop_later').click()
        # logger.debug('  wait for id "dropdown-menu"')
        # wait.until(
        #     EC.visibility_of_element_located((By.ID, 'dropdown-menu'))
        # )
        return self.is_element_present(By.ID, 'dropdown-menu')

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        driver.get("https://pc.moppy.jp/")
        pageobj = (By.ID, 'global-menu')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')

        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
