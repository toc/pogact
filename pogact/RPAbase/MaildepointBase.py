from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.RPAUserService import RPAUserService
from time import sleep

class MaildepointBase(RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ 楽天ウェブサーチにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://pointmall.rakuten.co.jp/mypage")
        #
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        if result is True:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
            driver.get("https://pointmall.rakuten.co.jp/mypage")
        #
        # ログイン
        po=(By.ID,"user_id")
        logger.debug(f'  wait for {po}')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['id'])
        #
        self.save_current_html('-0','html')
        #
        po=(By.CSS_SELECTOR,"#cta > div")
        logger.debug(f'  wait for {po}')
        wait.until(EC.element_to_be_clickable(po)).click()
        # パスワード
        po=(By.ID,"password_current")
        logger.debug(f'  wait for {po}')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(account['pw'])
        #
        self.save_current_html('-1','html')
        #
        # po=(By.CSS_SELECTOR,"#cta > div")  <- これではうまくアクセスできないので Full XPATH を利用。
        po=(By.XPATH,"/html/body/form/div/div[3]/div/div/div/div[2]/div/div/div[2]/div[5]/div")
        logger.debug(f'  wait for {po}')
        elem = driver.find_element(*po)
        for i in range(5):
            # ログインボタンの準備まち
            wk = elem.text
            logger.debug(f'  -- >{wk}<')
            if wk == "ログイン":
                break
            sleep(0.5)
        elem.click()
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

        ### ログアウトする
        driver.get("https://pointmall.rakuten.co.jp/mypage")
        #
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            driver.execute_script('closePR()')
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
