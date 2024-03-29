#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
        # 楽天ログイン ～ sso対応=infoseek経由
        self.pilot_logout()
        #
        logger.info(f"  -- あらためてログインを要求")
        driver.get("https://websearch.rakuten.co.jp/SimpleTop#")
        po = (By.LINK_TEXT, "ログイン")
        logger.debug(f'  wait for {po};')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_elements(*po)[0].click()
        #
        po = (By.ID, "scrollingLayer")
        logger.debug(f'  wait for {po}; ログイン画面')
        wait.until(EC.visibility_of_element_located(po))
        po = (By.CSS_SELECTOR, "#user_id")
        logger.debug(f'  wait for {po}; ユーザ入力')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['id'])
        # po = (By.CSS_SELECTOR, "#cta > div")
        po = (By.CSS_SELECTOR, "#cta001 > div > div")
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
        logger.info(f"  -- 状況にかかわらずログアウト要求を発行")
        driver.get("https://websearch.rakuten.co.jp/logout")
        po = (By.CSS_SELECTOR,'#status')
        wk1 = driver.find_element(*po).text
        self.assertEqual('ログアウトしました',wk1)
        #
        return True
