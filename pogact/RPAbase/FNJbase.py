from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import RPAbase.RPAbase


class FNJbase(RPAbase.RPAbase.RPAbase):
    """
    """
    def pilot_login(self, account):
        """ FNJの支払いページにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info(f"Try to login to FNJ(zeny).")
        # ==============================
        driver.get("https://zeny.cyberhome.ne.jp/user/login.aspx")
        logger.debug('  wait for (By.ID, u"LoginBody1_Tb_Account")')
        wait.until(EC.visibility_of_element_located((By.ID, "LoginBody1_Tb_Account")))
        driver.find_element(By.ID,"LoginBody1_Tb_Account").clear()
        driver.find_element(By.ID,"LoginBody1_Tb_Account").send_keys(account['id'])
        driver.find_element(By.ID,"LoginBody1_Tb_Passsword").clear()
        driver.find_element(By.ID,"LoginBody1_Tb_Passsword").send_keys(account['pw'])
        driver.find_element(By.ID,"LoginBody1_Btn_Login").click()
        logger.debug('  SUBMIT login.')

        logger.debug('  wait for link_text "取引内容の確認"')
        wait.until(
            EC.visibility_of_element_located(
                (By.LINK_TEXT, r'取引内容の確認')
            )
        )
        return self.is_element_present(By.LINK_TEXT, u"取引内容の確認")

    def pilot_logout(self):
        """
        Log-out from web site.
        """
        driver = self.driver
        logger = self.logger
        wait = self.wait

        logger.info(f"Try to logout from FNJ(zeny).")
        # ==============================
        driver.get('https://zeny.cyberhome.ne.jp/user/logout.aspx')
