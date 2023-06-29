#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RPAUserService import RPAUserService
import time

class ECnaviBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ siteにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://ecnavi.jp/login/")

        pageobj = (By.CSS_SELECTOR, '.global-header')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        wk = f'LINK_TEXT:ログアウト {"not" if result == False else ""} exists, ログイン{"中" if result else "前"}'
        logger.debug(f'  -- {wk}')
        if result == False:
            # Not logged-in.  Try to log-in to site.
            ### Original source codes for login.
            # ECnaviでも必要？
            if self.is_element_present(By.ID, 'PRmodal'):
                logger.warn('  PRmodal 発見。閉じます。')
                driver.execute_script('closePR()')

            # result = self.is_element_present(By.CSS_SELECTOR, ".c_button")
            pageobj = (By.NAME, 'email')
            logger.debug(f'  wait for {pageobj}')
            wait.until(EC.element_to_be_clickable(pageobj))
            driver.find_element(*pageobj).clear()
            driver.find_element(*pageobj).send_keys(account['id'])
            pageobj = (By.NAME, 'passwd')
            driver.find_element(*pageobj).clear()
            driver.find_element(*pageobj).send_keys(account['pw'])
            time.sleep(1.5)
            # pageobj = (By.CSS_SELECTOR, '#recaptcha-anchor')
            pageobj = (By.ID, 'recaptcha-anchor')
            driver.find_element(*pageobj).click()

            driver.find_element(By.CSS_SELECTOR,".c_button").click()
            logger.debug('  SUBMIT login.')
            ###
            # ECnaviでも必要？
            if self.is_element_present(By.ID, 'modalTop'):
                logger.warn('  modalTop 発見。閉じます。')
                driver.find_element(By.ID, 'modalTop_later').click()
        else:
            logger.debug(f'  Do not LOGIN, because i use profile registration.')
            logger.debug(f'  Go to top page of target site.')

        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        wk = f'LINK_TEXT:ログアウト {"not" if result == False else ""} exists, ログイン{"中" if result else "前"}'
        logger.debug(f'  -- {wk}')

        # return self.is_element_present(By.ID, 'dropdown-menu')
        return result


    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.debug(f'  Do not LOGOUT, because i use profile registration.')

        # driver.get("https://ecnavi.jp/logout/")
        # pageobj = (By.ID, 'global-header')
        # logger.debug(f'  wait for {pageobj}')
        # wait.until(EC.visibility_of_element_located(pageobj))

        # if driver.is_alert_present():
        #     self.assertEqual(u"ログアウトしますか？", self.close_alert_and_get_its_text())
        # # ECnaviでも必要？
        # # if self.is_element_present(By.ID, 'PRmodal'):
        # #     logger.warn('  PRmodal 発見。閉じます。')
        # #     driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        wk = f'LINK_TEXT:ログアウト {"not" if result == False else ""} exists, ログイン{"中" if result else "前"}'
        logger.debug(f'  -- {wk}')

        # ログイン状態にかかわらず True をかえす
        return True

