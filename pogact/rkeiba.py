# -*- coding: utf-8 -*-
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from logging import DEBUG, INFO    # , WARNING, ERROR, CRITICAL
import yaml
import datetime
import time
# from logutils import logger
import logutils.AppDict
from logutils import mailreporter
import RPAbase.RakutenBase
# from RPAbase.RakutenBase import RakutenBase


class Rkeiba(RPAbase.RakutenBase.RakutenBase):
    """
    """
    def __init__(self):
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            r'Rkeiba', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.reporter = mailreporter.MailReporter(r'smtpconf.yaml', self.appdict.name)

    def prepare(self):
        super().prepare(self.appdict.name)
        self.today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        self.logger.debug(f"{self.today.strftime('%c')}")
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return super().pilot_setup(options)

    def pilot_depositing(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info('  入金処理開始')
        # ==============================
        driver.get('https://keiba.rakuten.co.jp/')
        logger.debug('  wait for (By.LINK_TEXT, u"入金")')
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, u"入金")))
        driver.find_element_by_link_text(u"入金").click()
        # ポップアップに移動
        logger.debug('  wait for NEW POPUP WINDOW.')
        wait.until(lambda d: len(d.window_handles) > 1)
        logger.debug('  switch to NEW POPUP WINDOW.')
        driver.switch_to.window(driver.window_handles[1])
        #
        logger.info('  入金額指定')
        # ==============================
        logger.debug('  wait for (By.ID, "depositingInputPrice")')
        wait.until(EC.element_to_be_clickable((By.ID, "depositingInputPrice")))
        driver.find_element_by_id("depositingInputPrice").click()
        driver.find_element_by_id("depositingInputPrice").clear()
        driver.find_element_by_id("depositingInputPrice").send_keys(user['charge'])
        driver.find_element_by_id("radioMail01").click()
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='※混雑時の入金処理には、数十分程度かかることがあります。余裕を持って、入金指示を行なってください。'])[1]/following::span[1]").click()
        #
        logger.info('  入金指定確認＆実行！')
        # ==============================
        logger.debug('  wait for (By.NAME, "pin")')
        wait.until(EC.element_to_be_clickable((By.NAME, "pin")))
        driver.find_element_by_name("pin").click()
        driver.find_element_by_name("pin").clear()
        driver.find_element_by_name("pin").send_keys(user['pin'])
        driver.find_element_by_id("depositingOmitFlg").click()
        logger.debug('  SUBMIT depositing.')
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='戻る'])[1]/following::span[1]").click()
        logger.debug('  wait until: element_to_be_clickable((By.LINK_TEXT, u"投票画面へ"))')
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, u"投票画面へ"))).click()

    def check_balance(self):
        """
        Check current balance and return it as integer.
        This function assumes that top page of Rakuten keiba was already loaded.
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug(f'  @@START check balance')
        
        logger.debug(f'  - wait.until(EC.visibility_of_element_located((By.LINK_TEXT,"更新")))')
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT,'更新'))).click()
        wk = driver.find_element_by_xpath('//*[@id="balanceStatus"]/ul/li[3]/span/span[2]').text
        logger.debug(f'  - current balance: >{wk}<')
        balance = 0 if wk == '---' else int(wk.replace(',', ''))

        logger.debug(f'  @@END check balance')
        return balance

    def pilot(self):
        driver, wait = self.pilot_setup()
        logger = self.logger

        need_report = 0

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users = self.config.get('users',{})
        users_rakuten = users.get('Rakuten',[])
        # Get service information
        svcs = self.config.get('services',{})
        svcs_rkeiba = svcs.get('Rkeiba',[])
        if len(users_rakuten) * len(svcs_rkeiba) == 0:
            self.logger.warn(f"No user({len(users_rakuten)}) or service({len(svcs_rkeiba)}) is found.  exit.")
            return

        # main loop
        for user in users_rakuten:
            logger.info(f"処理開始: user={user['name']}")
            # ==============================
            if user['name'] not in svcs_rkeiba:
                logger.info(f"- User {user['name']} does not use this service.  Skip.")
                continue

            logger.debug(f" 設定内容確認開始")
            # ==============================
            # 金額未指定ならデフォルト値(100円)
            user['charge'] = user.get('charge', 100)
            # パスワード, pin 以外をデバッグログに出力
            wk = {k:v for (k,v) in user.items() if k in ('name','id')}
            logger.debug(f"  params: {wk}")
            # 実行記録を確認：当日中の実行は１回に限定したい
            who = user['id']
            last_dones = self.last_done.get('Rkeiba',{})
            last_done = last_dones.get(who)
            if type(last_done) is not datetime.datetime: last_done = datetime.datetime.min
            logger.debug(f" {who}: today={self.today} vs last={last_done}")
            if self.today < last_done:
                logger.info(f" {who}: Already done today.  SKIP.")
                self.pilot_result.append(
                    f"{user['name']}: Already done today.  SKIP."
                )
                continue

            need_report += 1
            try:
                logger.info(' 楽天競馬にログイン')
                # ==============================
                if self.pilot_login(user):
                    # login succeed.
                    driver.get('https://keiba.rakuten.co.jp/')
                    balance_old = self.check_balance()

                    logger.info(' 入金処理')
                    # ==============================
                    self.pilot_depositing(user)

                    logger.info(' 入金完了確認')
                    # ==============================
                    result_msg = f"{user['name']}: {balance_old} is not changed."
                    driver.get('https://keiba.rakuten.co.jp/')      # for self.check_balance()
                    for i in range(8):
                        time.sleep(5)
                        balance_new = self.check_balance()
                        logger.info(f"  {i}: {balance_old}->{balance_new}")

                        if balance_new > balance_old:
                            last_dones[who] = datetime.datetime.now()
                            self.last_done['Rkeiba'] = last_dones
                            logger.info(f" {who}: Complete at {last_dones[who].strftime('%c')}.")
                            result_msg = f"{user['name']}: {balance_old}->{balance_new}"
                            break
                    self.pilot_result.append(result_msg)
                else:
                    # login failed
                    pass

            except (TimeoutException, NoSuchElementException) as e:
                self.pilot_result.append(f"{user['name']}: Ex={type(e)}")
                logger.error(e.args)
            except Exception as e:
                self.pilot_result.append(f"{user['name']}: Ex={type(e)} {e.args}")
                # self.pilot_result.append(f"{user['name']}: Unexpected error: {sys.exc_info()[0]}")
                logger.critical(f"Exception: {type(e)} {e.args}")
            finally:
                logger.info(' ポップアップ終了～ログアウト')
                # ==============================
                logger.debug(f"  片づけ開始: {driver.window_handles}")
                if len(driver.window_handles) > 1:
                    for window in driver.window_handles[1:]:
                        logger.debug(f"  Close request -> <{window}>")
                        driver.switch_to.window(window)
                        driver.close()
                logger.debug(f"  片づけ完了: {driver.window_handles}")
                driver.switch_to.window(driver.window_handles[0])
                self.pilot_logout()

            logger.info(f"処理完了: user={user['name']}")

        logger.info(f"全処理を完了")
        # ==============================
        self.tearDown()
        
        logger.info(f" 処理結果: {self.pilot_result}, need_report: {need_report}")
        if need_report > 0 and self.pilot_result != []:
            self.reporter.report(f" 処理結果: {self.pilot_result}")
            logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")


if __name__ == "__main__":
    App = Rkeiba()
    App.prepare()
    App.pilot()
