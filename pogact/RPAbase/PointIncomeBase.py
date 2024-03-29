#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RPAUserService import RPAUserService


class PointIncomeBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ ポイントインカムにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://pointi.jp/entrance.php")
        pageobj = (By.ID, 'logo_box')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        # if self.is_element_present(By.ID, 'PRmodal'):
        #     logger.warn('  PRmodal 発見。閉じます。')
        #     driver.execute_script('closePR()')
        po = (By.CSS_SELECTOR, '#outer > div.entrance_wrap > div:nth-child(1) > div.entform_box > form > input[type=submit]')
        result = self.is_element_present(*po)
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()

        pageobj = (By.NAME, 'email_address')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.element_to_be_clickable(pageobj))
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.NAME, 'password')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])

        import time
        time.sleep(5)

        driver.find_element(By.CSS_SELECTOR,".entform_box > form:nth-child(1) > input:nth-child(2)").click()
        # "".a-btn__login").click()
        logger.debug('  SUBMIT login.')
        ###
        pageobj = (By.TAG_NAME, 'body')
        wait.until(EC.visibility_of_element_located(pageobj))
        if self.is_element_present(By.ID, 'recommen_modal'):
            logger.warn('  modalTop 発見。閉じます。')
            driver.find_element(By.ID, 'cboxClose').click()
        # logger.debug('  wait for id "dropdown-menu"')
        # wait.until(
        #     EC.visibility_of_element_located((By.ID, 'dropdown-menu'))
        # )
        return self.is_element_present(By.LINK_TEXT, 'マイページ')

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        driver.get("https://pointi.jp/")
        pageobj = (By.ID, 'logo_box')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        if self.is_element_present(By.ID, 'recommen_modal'):
            logger.warn('  modalTop 発見。閉じます。')
            driver.find_element(By.ID, 'cboxClose').click()

        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.LINK_TEXT,u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result


