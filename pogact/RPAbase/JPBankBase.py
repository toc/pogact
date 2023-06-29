import time
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import RPAbase.RPAUserService


class JPBankBase(RPAbase.RPAUserService.RPAUserService):
    """
    """
    def pilot_login(self, account):
        """ ゆうちょ銀行 にログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://direct.jp-bank.japanpost.jp/tp1web/U010101WAK.do?link_id=ycDctLgn#")
        logger.debug('  wait for (By.ID, "header")')
        wait.until(EC.visibility_of_element_located((By.ID, 'header')))
        logger.debug('  wait for (By.ID, "strMain")')
        wait.until(EC.visibility_of_element_located((By.ID, 'strMain')))

        wk = account['id']
        # logger.debug('  wait for visibility_of_element_located((By.NAME, "okyakusamaBangou1")')
        # wait.until(EC.visibility_of_element_located((By.NAME, "okyakusamaBangou1")))
        logger.debug('  wait for element_to_be_clickable((By.NAME, "okyakusamaBangou1")')
        wait.until(EC.element_to_be_clickable((By.NAME, "okyakusamaBangou1")))
        elm = driver.find_element(By.NAME,"okyakusamaBangou1")
        elm.click()
        # logger.debug('  click1')
        elm.clear()
        # logger.debug('  clear1')
        elm.send_keys(wk[0:4])
        # logger.debug('  send_key1')
        logger.debug('  wait for element_to_be_clickable((By.NAME, "okyakusamaBangou2")')
        wait.until(EC.element_to_be_clickable((By.NAME, "okyakusamaBangou2")))
        elm = driver.find_element(By.NAME,"okyakusamaBangou2")
        elm.clear()
        elm.send_keys(wk[4:8])
        logger.debug('  wait for element_to_be_clickable((By.NAME, "okyakusamaBangou3")')
        wait.until(EC.element_to_be_clickable((By.NAME, "okyakusamaBangou3")))
        elm = driver.find_element(By.NAME,"okyakusamaBangou3")
        elm.clear()
        elm.send_keys(wk[8:13])
        driver.find_element(By.NAME,"U010103").click()

        regex1 = re.compile("^合言葉")
        while True:
            logger.debug('  wait for (By.ID, "strMain")')
            wait.until(EC.visibility_of_element_located((By.ID, 'strMain')))
            # /html/body/form[1]/div[3]/div[2]/div[1]/table/tbody/tr/th/text()
            # strMain > table > tbody > tr > th
            if self.is_element_present(By.CSS_SELECTOR,"#strMain > table > tbody > tr > th"):

                th = driver.find_element(By.CSS_SELECTOR,"#strMain > table > tbody > tr > th").text
                logger.debug(f'  -- th: {th.splitlines()[0]}')
                if regex1.match(th):
                    question = driver.find_element(By.CSS_SELECTOR,"#strMain > table > tbody > tr > td > dl > dd:nth-child(2)").text
                    logger.debug(f'  -- q: {question}')
                    ans = account['hint'][question]
                    logger.debug(f'  -- a: {ans}')
                    elm = driver.find_element(By.NAME,"aikotoba")
                    elm.clear()
                    elm.send_keys(ans)
                    driver.find_element(By.LINK_TEXT,"次へ").click()
                    time.sleep(0.5)
            else:
                # パスワード入力画面のハズ
                break

        logger.debug('  wait for visibility_of_element_located((By.NAME, "loginPassword")')
        wait.until(EC.visibility_of_element_located((By.NAME, "loginPassword")))
        elm = driver.find_element(By.NAME,"loginPassword")
        elm.clear()
        elm.send_keys(account['pw'])
        driver.find_element(By.NAME,"U010302").click()

        # 画面遷移待ち: PCサイトだとPhishwallを入れろと迫ってくる
        logger.debug('  wait for link_text "ログアウト"')
        wait.until(
            EC.visibility_of_element_located((By.LINK_TEXT, r'ログアウト'))
        )
        if self.is_element_present(By.LINK_TEXT, '後でインストールします。（次へ）'):
            driver.find_element(By.LINK_TEXT,"後でインストールします。（次へ）").click()
            # もう一度、ログアウトLINKを待つ
            logger.debug('  wait for link_text "ログアウト"(2回目)')
            wait.until(
                EC.visibility_of_element_located((By.LINK_TEXT, r'ログアウト'))
            )

        ### 処理終了
        return self.is_element_present(By.LINK_TEXT, u"ログアウト")

    def pilot_logout(self,account):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        ### ゆうちょダイレクト からのログアウト
        # driver.get("https://my.mineo.jp/")
        # wait.until(EC.visibility_of_element_located((By.ID, 'header')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element(By.LINK_TEXT,u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result
