from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base.RPAbase import RPAbase
import time

class Nanaco(RPAbase):
    """
    """
    def pilot_login(self, account):
        """ nanacoにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info("  Try to login at https://www.nanaco-net.jp/pc/emServlet")
        driver.get("https://www.nanaco-net.jp/pc/emServlet")
        logger.debug("  wait for (By.ID, \"nanacoMember\")")
        wait.until(EC.visibility_of_element_located((By.ID, "nanacoMember")))
        if self.is_element_present(By.LINK_TEXT, "ログアウト"):
            logger.debug(f'  -- Logout first, because there is LOGOUT link.')
            self.pilot_logout(account)
        # ----
        logger.info("  -- Input card-number, security-code")
        driver.find_element_by_name("XCID").send_keys(account['id'])
        driver.find_element_by_name("SECURITY_CD").send_keys(account['pw'])
        # ----
        logger.debug("  -- Click SUBMIT.")
        wait.until(EC.visibility_of_element_located((By.NAME, "ACT_ACBS_do_LOGIN2"))).click()


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
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
