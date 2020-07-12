from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import random
import RPAbase.RPAbase
import logutils.mailreporter


class RCardBase(RPAbase.RPAbase.RPAbase):
    """
    """
    def prepare(self, name=__name__, reporter_subject=None):
        super().prepare(name)
        try:
            subject = reporter_subject if reporter_subject else self.appdict.name
            self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', subject)
        except Exception as e:
            self.logger.warn(f'Caught Exception: {type(e)} {e.args if hasattr(e,"args") else str(e)}')
            self.reporter = None

    def report(self, msg=None, subject=None):
        if msg is None:
            msg = self.pilot_result
        if self.reporter is not None:
            self.reporter.report(msg)

    def pilot_login(self, account):
        """ 楽天カードにログイン """
        ## 楽天市場でログインしてても楽天カードに移動すると再ログイン必要だが、
        ## 楽天カードにログインしてから楽天市場に移動すると再ログイン不要っぽい。
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://www.rakuten-card.co.jp/e-navi/")
        logger.debug('  wait for (By.ID, r"header")')
        wait.until(EC.visibility_of_element_located((By.ID, r'header')))
        result = self.is_element_present(By.ID, r'loginButton')
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        logger.debug('  wait for (By.ID, r"linkButton")')
        wait.until(EC.element_to_be_clickable((By.ID, r'loginButton')))

        driver.find_element_by_id("u").clear()
        driver.find_element_by_id("u").send_keys(account['id'])
        driver.find_element_by_id("p").clear()
        driver.find_element_by_id("p").send_keys(account['pw'])
        driver.find_element_by_id("loginButton").click()
        ###
        logger.debug('  wait for link_text "ログアウト"')
        wait.until(
            EC.visibility_of_element_located(
                (By.LINK_TEXT, r'ログアウト')
            )
        )
        return self.is_element_present(By.LINK_TEXT, u"ログアウト")

    def pilot_logout(self, account):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### 楽天競馬のオートパイロットからパクリ
        driver.get("https://www.rakuten-card.co.jp/e-navi/members/index.xhtml")
        wait.until(EC.visibility_of_element_located((By.ID, 'headArea')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
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
        users = users_grp.get('Rakuten',[])          # app group
        # Get service information
        svcs_grp = self.config.get('services',{})
        svcs = svcs_grp.get(appdict.name,[])             # app name
        if len(users) * len(svcs) == 0:
            self.logger.warn(f"No user({len(users)}) or service({len(svcs)}) is found.  exit.")
            return

        # main loop
        random.shuffle(users)
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
