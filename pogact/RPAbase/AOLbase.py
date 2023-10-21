#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import RPAbase.RPAbaseRecapture

class AOLbase(RPAbase.RPAbaseRecapture.RPAbaseRecapture):
    """
    """
    def pilot_login(self, account):
        """ AOLにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        #
        self.pilot_logout(account)
        #
        logger.info('-- driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")')
        driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")

        pageobj = (By.TAG_NAME, "body")
        logger.info('-- visibility_of_element_located(By.TAG, "body")')
        wait.until(EC.visibility_of_element_located(pageobj))

        if self.is_element_present(*pageobj):
            logger.info('-- Try to log-in.')
            pageobj = (By.NAME, "username")
            driver.find_element(*pageobj).clear()
            driver.find_element(*pageobj).send_keys(account['id'])
            pageobj = (By.NAME, "signin")
            driver.find_element(*pageobj).click()

            pageobj = (By.NAME, "password")
            wait.until(EC.visibility_of_element_located(pageobj))
            driver.find_element(*pageobj).clear()
            driver.find_element(*pageobj).send_keys(account['pw'])
            pageobj = (By.NAME, "verifyPassword")
            driver.find_element(*pageobj).click()

        pageobj = (By.TAG_NAME, "body")
        logger.info('-- visibility_of_element_located(By.TAG, "body")')
        wait.until(EC.visibility_of_element_located(pageobj))

        return True


    def pilot_logout(self, account):
        """ AOLからログアウト """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        result = False

        pageobj = (By.LINK_TEXT, "ログアウト")
        if self.is_element_present(*pageobj) is False:
            logger.debug(f'-- driver.get("https://www.aol.jp/https://mail.aol.com/webmail-std/ja-jp/suite")')
            driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")

        try:
            logger.info('-- Try to log-out.')
            logger.debug(f'-- wait for [{pageobj}]')
            wait.until(EC.visibility_of_element_located(pageobj))
            driver.find_element(*pageobj).click()

            pageobj = (By.TAG_NAME, 'body')
            logger.debug(f'-- wait for [{pageobj}]')
            wait.until(EC.visibility_of_element_located(pageobj))
            # driver.find_element(*pageobj).click()

            try:
                pageobj = (By.PARTIAL_LINK_TEXT, 'row_count = len(rows)')
                logger.debug(f'-- wait for [{pageobj}]')
                wait.until(EC.visibility_of_element_located(pageobj))
            except TimeoutException as e:
                pageobj = (By.PARTIAL_LINK_TEXT, 'サインイン')
                logger.debug(f'-- wait for [{pageobj}]')
                wait.until(EC.visibility_of_element_located(pageobj))

            result = True

        except Exception as e:
            logger.error(self.exception_message(e))

        return result

    def pilot(self):
        # driver, wait = self.pilot_setup()
        logger = self.logger
        appdict = self.appdict

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users_grp = self.config.get('users',{})
        users = users_grp.get(appdict.user_group,[])          # app group
        # Get service information
        svcs_grp = self.config.get('services',{})
        svcs = svcs_grp.get(appdict.name,[])             # app name
        if len(users) * len(svcs) == 0:
            self.logger.warn(f"No user({len(users)}) or service({len(svcs)}) is found.  exit.")
            return

        # main loop
        for user in users:
            wk = ( str(user.get("name","")), str(user.get("id","")) )
            logger.info(f'処理開始: user=[name=>{wk[0]}<, id=>{wk[1]}<]')
            # ==============================
            if wk[0] not in svcs:
                logger.info(f"- User >{wk[0]}< does not use this service.  Skip.")
                continue
            #
            driver, wait = self.pilot_setup(wk[0])

            logger.info('-- driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")')
            driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")

            logger.debug(f'1.ログイン')
            # ==============================
            self.pilot_login(user)
            #
            logger.debug(f'2.処理本体')
            # ==============================
            self.pilot_internal(user)
            #
            logger.debug(f'3.ログアウト')
            # ==============================
            self.pilot_logout(user)

            driver.quit
