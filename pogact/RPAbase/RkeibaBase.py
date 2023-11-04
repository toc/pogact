#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
        #
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
        driver.find_element(By.LINK_TEXT,"マイページログイン").click()
        #
        po = (By.ID, "scrollingLayer")
        logger.debug(f'  wait for {po}; ログイン画面')
        wait.until(EC.visibility_of_element_located(po))
        po = (By.CSS_SELECTOR, "#user_id")
        logger.debug(f'  wait for {po}; ユーザ入力')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['id'])
        driver.find_element(*po).send_keys(Keys.ENTER)
        # ----
        po = (By.CSS_SELECTOR, "#password_current")
        logger.debug(f'  wait for {po}; PW入力')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['pw'])
        driver.find_element(*po).send_keys(Keys.ENTER)
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
        #
        ### Logout
        logger.info(f"  -- 状況にかかわらずログアウト要求を発行")
        driver.get("https://bet.keiba.rakuten.co.jp/login/logout")
        po = (By.CSS_SELECTOR,'#container > div.logoutbody > p')
        wk1 = driver.find_element(*po).text
        self.assertEqual('ログアウトしました',wk1)
        #
        driver.get("https://keiba.rakuten.co.jp/")
        #
        return True
