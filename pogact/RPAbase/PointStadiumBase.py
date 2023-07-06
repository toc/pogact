from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService


class PointStadiumBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ ポイントスタジアムにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://www.point-stadium.com/loginw.asp")
        pageobj = (By.XPATH, "//img[@alt='ポイントスタジアム']")
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        # if self.is_element_present(By.ID, 'PRmodal'):
        #     logger.warn('  PRmodal 発見。閉じます。')
        #     driver.execute_script('closePR()')
        po = (By.XPATH, "//img[@alt='ログアウト']")
        result = self.is_element_present(*po)
        if result is True:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        #
        driver.get("https://www.point-stadium.com/loginw.asp")
        pageobj = (By.ID, 'mailadr')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.element_to_be_clickable(pageobj))
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.ID, 'passwd')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])
        # import time
        # time.sleep(5)
        pageobj = (By.XPATH, "//div[@id='main_sub']/p/a/img")
        driver.find_element(*pageobj).click()
        logger.debug('  SUBMIT login.')
        ###
        pageobj = (By.TAG_NAME, 'body')
        wait.until(EC.visibility_of_element_located(pageobj))
        # if self.is_element_present(By.ID, 'recommen_modal'):
        #     logger.warn('  modalTop 発見。閉じます。')
        #     driver.find_element(By.ID, 'cboxClose').click()
        # po = (By.XPATH, "//img[@alt='ログアウト']")
        po = (By.CSS_SELECTOR,'.logout')
        logger.debug(f'  wait for {po}')
        wait.until(
            EC.visibility_of_element_located(po)
        )
        return self.is_element_present(*po)

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        driver.get("https://www.point-stadium.com/")
        pageobj = (By.XPATH, "//img[@alt='ポイントスタジアム']")
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        # if self.is_element_present(By.ID, 'recommen_modal'):
        #     logger.warn('  modalTop 発見。閉じます。')
        #     driver.find_element(By.ID, 'cboxClose').click()

        # po = (By.XPATH, "//img[@alt='ログアウト']")
        po = (By.CSS_SELECTOR,'.logout')
        result = self.is_element_present(*po)
        logger.debug(f"  -- {po} exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(*po).click()
        else:   
            logger.debug(f"  -- Do nothing and exit.")
        return result


