from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService


class RkeibaBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ 楽天ウェブサーチにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://keiba.rakuten.co.jp/")
        logger.debug('  wait for (By.LINK_TEXT, u"トップ")')
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, u"トップ")))
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"マイページログイン")
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        logger.debug('  wait for (By.LINK_TEXT,u"マイページログイン")')
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, u"マイページログイン")))
        driver.find_element_by_link_text(u"マイページログイン").click()
        # with codecs.open("temp.html", "w", "cp932", 'ignore') as f:
        #     f.write(driver.page_source)
        logger.debug('  wait for (By.ID, "loginInner_u")')
        wait.until(EC.element_to_be_clickable((By.ID, "loginInner_u")))
        driver.find_element_by_id("loginInner_u").clear()
        driver.find_element_by_id("loginInner_u").send_keys(account['id'])
        driver.find_element_by_id("loginInner_p").clear()
        driver.find_element_by_id("loginInner_p").send_keys(account['pw'])
        driver.find_element_by_name("submit").click()
        logger.debug('  SUBMIT login.')
        ###
        logger.debug('  wait for link_text "ログアウト"')
        wait.until(
            EC.visibility_of_element_located(
                (By.LINK_TEXT, r'ログアウト')
            )
        )
        return self.is_element_present(By.LINK_TEXT, u"ログアウト")

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### 楽天競馬のオートパイロットからパクリ
        driver.get("https://keiba.rakuten.co.jp/")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.glonavmain')))
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
