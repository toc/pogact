#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import RPAbase.RPAUserService


class RBankBase(RPAbase.RPAUserService.RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ 楽天銀行にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://fes.rakuten-bank.co.jp/MS/main/RbS?CurrentPageID=START&&COMMAND=LOGIN")
        pageobj = (By.CSS_SELECTOR, '#LOGIN\:USER_ID')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['id'])
        pageobj = (By.CSS_SELECTOR, '#LOGIN\:LOGIN_PASSWORD')
        driver.find_element(*pageobj).clear()
        driver.find_element(*pageobj).send_keys(account['pw'])
        pageobj = (By.LINK_TEXT, 'ログイン')
        driver.find_element(*pageobj).click()
        ###
        pageobj = (By.LINK_TEXT, 'ログアウト')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))

        return self.is_element_present(By.LINK_TEXT, u"ログアウト")


    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait
        #
        logger.info( f'  楽天銀行からログアウト')
        # ==============================
        logger.debug(f'  - 移動: 商品･サービス一覧')
        po = (By.PARTIAL_LINK_TEXT,'サービス一覧')
        wait.until(EC.element_to_be_clickable(po))
        driver.find_element(*po).click()
        # ------------------------------
        logger.debug(f'  - ボタン押下: ログアウト')
        pageobj = (By.LINK_TEXT,'ログアウト')
        logger.debug(f'  wait for {pageobj}')
        wait.until(EC.visibility_of_element_located(pageobj))
        driver.find_element(*pageobj).click()
        # ------------------------------
        logger.debug(f'  - 継続確認: ログアウト')
        # pageobj = (By.CSS_SELECTOR,'#LOGOUT_COMFIRM')            
        pageobj = (By.CSS_SELECTOR,'#j_id_3a')            
        result = self.is_element_present(*pageobj)
        logger.debug(f'  wait for {pageobj}')
        logger.debug(f"  -- {pageobj} exists? {result}")
        wait.until(EC.visibility_of_element_located(pageobj))
        driver.find_element(*pageobj).click()
        #
        logger.debug(f'ログアウト確認')
        # ==============================
        pageobj = (By.CSS_SELECTOR, '#str-main')
        wait.until(EC.visibility_of_element_located(pageobj))
        wk = driver.find_element(*pageobj).text
        result = True if re.match('ログアウトしました。', wk) else False
        logger.debug(f'  [{result}]: >{wk.split()[0]}<')
        #
        return result

