from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import RPAbase.RPAbaseRecapture
import time

class AOLbase(RPAbase.RPAbaseRecapture.RPAbaseRecapture):
    """
    """
    def pilot_login(self, account):
        """ AOLにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info('-- driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")')
        driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")

        pageobj = (By.TAG_NAME, "body")
        logger.info('-- visibility_of_element_located(By.TAG, "body")')
        wait.until(EC.visibility_of_element_located(pageobj))

        if self.is_element_present(*pageobj):
            logger.info('-- Try to log-in.')
            pageobj = (By.NAME, "username")
            driver.find_element(*pageobj).send_keys(account['id'])
            pageobj = (By.NAME, "signin")
            driver.find_element(*pageobj).click()

            pageobj = (By.NAME, "password")
            wait.until(EC.visibility_of_element_located(pageobj))
            driver.find_element(*pageobj).send_keys(account['pw'])
            pageobj = (By.NAME, "verifyPassword")
            driver.find_element(*pageobj).click()

        pageobj = (By.TAG_NAME, "body")
        logger.info('-- visibility_of_element_located(By.TAG, "body")')
        wait.until(EC.visibility_of_element_located(pageobj))

        return True


    def pilot_logout(self, account):
        # Do nothing
        return True

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