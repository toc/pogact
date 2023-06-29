#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RPAUserService import RPAUserService


class SBIgroupBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ SBIポイントにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        # ログイン状態チェック
        driver.get("https://sbipoint.jp/")
        pageobj = (By.CSS_SELECTOR, '#header')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        # if self.is_element_present(By.ID, 'PRmodal'):
        #     logger.warn('  PRmodal 発見。閉じます。')
        #     driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        if result is True:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()

        # ログイン実行
        driver.get("https://id.sbigroup.jp/login/index2")
        pageobj = (By.NAME, 'loginMail')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.element_to_be_clickable(pageobj))
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.NAME, 'pass1')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])

        driver.find_element(By.CSS_SELECTOR,".btn-primary").click()
        logger.debug('  SUBMIT login.')
        ###
        # if self.is_element_present(By.ID, 'modalTop'):
        #     logger.warn('  modalTop 発見。閉じます。')
        #     driver.find_element(By.ID, 'modalTop_later').click()

        pageobj = (By.CSS_SELECTOR, '#global-nav')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        return self.is_element_present(*pageobj)

    def pilot_logout(self, account=None):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        driver.get("https://sbipoint.jp/")
        pageobj = (By.CSS_SELECTOR, '#header')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        # if self.is_element_present(By.ID, 'PRmodal'):
        #     logger.warn('  PRmodal 発見。閉じます。')
        #     driver.execute_script('closePR()')

        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.LINK_TEXT,u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
