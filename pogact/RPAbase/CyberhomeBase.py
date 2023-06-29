#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import RPAbase.RPAUserService


class CyberhomeBase(RPAbase.RPAUserService.RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ Cyberhome mailページにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info(f"Try to login to FNJ(cyberhome mail).")
        # ==============================
        driver.get("https://wmail.cyberhome.ne.jp/login/")
        logger.debug('  wait for (By.ID, u"username")')
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        u = driver.find_element(By.ID,"username")
        u.clear()
        u.send_keys(account['id'])
        p = driver.find_element(By.ID,'password')
        p.clear()
        p.send_keys(account['pw'])

        logger.debug('  SUBMIT login.')
        driver.find_element(By.XPATH,u"//img[@alt='ログイン']").click()
        logger.debug(f' --wait.until element_to_be_clickable((By.ID,r"menu_mail_inbox_unread"))')
        wait.until(EC.element_to_be_clickable((By.ID,r"menu_mail_inbox_unread")))
        
        return self.is_element_present(By.LINK_TEXT, u"新着をチェック")

    def pilot_logout(self, account=None):
        """
        Log-out from web site.
        """
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.info(f"Try to logout from FNJ(cyberhome mail).")
        # ==============================
        driver.get('https://wmail.cyberhome.ne.jp/logout/')
