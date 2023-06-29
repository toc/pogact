#! /usr/bin/env python
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import RPAbase.RPAbase

class Nanaco(RPAbase.RPAbase.RPAbase):
    """
    """
    def pilot_login(self, account):
        """ nanacoにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info("  Try to login at https://www.nanaco-net.jp/pc/emServlet")
        driver.get("https://www.nanaco-net.jp/pc/emServlet")
        po = (By.ID,'loginByPassword')
        logger.debug(f"  wait for {po}")
        wait.until(EC.visibility_of_element_located(po))
        if self.is_element_present(By.LINK_TEXT, "ログアウト"):
            logger.debug(f'  -- Logout first, because there is LOGOUT link.')
            self.pilot_logout(account)
        # ----
        logger.info("  -- Input card-number, security-code")
        po = (By.XPATH,'//*[@id="login_password"]/table/tbody/tr[1]/td[2]/input')
        driver.find_element(*po).send_keys(account['id'])
        po = (By.XPATH,'//*[@id="login_password"]/table/tbody/tr[2]/td[2]/input')
        driver.find_element(*po).send_keys(account['pw'])
        # ----
        logger.debug("  -- Click SUBMIT.")
        wait.until(EC.visibility_of_element_located((By.NAME, "ACT_ACBS_do_LOGIN1"))).click()


    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### 作業ページからログアウトする
        ### ログアウトリンクが現在のページに存在していることが前提
        logger.info("  Try to logout from current page.")
        # ボツ↓: トップページを開くとセッションが切れてログイン状態が継続しない。
        # driver.get("https://www.nanaco-net.jp/pc/emServlet")
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, 'ログアウト')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.LINK_TEXT,"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result

    def pilot(self):
        driver, wait = self.pilot_setup()
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

        # logger.info(f"全処理を完了")
        # # ==============================
        # self.tearDown()
        
        # logger.info(f" 処理結果: {self.pilot_result}, need_report: {need_report}")
        # if need_report > 0 and self.pilot_result != []:
        #     self.reporter.report(f" 処理結果: {self.pilot_result}")
        #     logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")
