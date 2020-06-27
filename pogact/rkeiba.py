# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from logging import DEBUG, INFO    # , WARNING, ERROR, CRITICAL
import yaml
import datetime
import time
from logutils import logger
from logutils import mailreporter


class Rkeiba():
    def setup(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(20)
        self.wait = WebDriverWait(self.driver, 20)
        self.pilot_record = []
        self.accept_next_alert = True
        self.logger = logger.Logger('Rkeiba', clevel=INFO, flevel=DEBUG, path=r'logs')
        self.reporter = mailreporter.MailReporter(r'smtpconf.yaml', r'RKeiba')

        self.today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        self.logger.debug(f"{self.today.strftime('%c')}")
        try:
            with open('last_done.yaml', 'r', encoding='utf-8') as f:
                self.last_done = yaml.safe_load(f)
        except:
            self.last_done = {}
        try:
            with open('settings.yaml', 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}
        return

    def pilot_login(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://keiba.rakuten.co.jp/")
        logger.debug('  wait for (By.LINK_TEXT, u"トップ")')
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, u"トップ")))
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            # driver.find_element_by_css_selector('#PRmodal > div:nth-child(4)').click()
            driver.find_element_by_xpath('/html/body/section/div[2]/div').click()
        result = self.is_element_present(By.LINK_TEXT, u"マイページログイン")
        if result is False:
            logger.info(f"  -- ログイン中のようなので 一旦 ログアウトします")
            self.pilot_logout()
        logger.debug('  wait for (By.LINK_TEXT,u"マイページログイン")')
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, u"マイページログイン")))
        driver.find_element_by_link_text(u"マイページログイン").click()
        logger.debug('  wait for (By.ID, "loginInner_u")')
        wait.until(EC.element_to_be_clickable((By.ID, "loginInner_u")))
        driver.find_element_by_id("loginInner_u").clear()
        driver.find_element_by_id("loginInner_u").send_keys(user['id'])
        driver.find_element_by_id("loginInner_p").clear()
        driver.find_element_by_id("loginInner_p").send_keys(user['pw'])
        driver.find_element_by_name("submit").click()
        logger.debug('  SUBMIT login.')
        logger.debug('  wait for 現在残高<XPATH>')
        wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, r'//*[@id="balanceStatus"]/ul/li[3]/span/span[2]')
            )
        )
        # 現在残高を確認
        wk = driver.find_element_by_xpath(
            r'//*[@id="balanceStatus"]/ul/li[3]/span/span[2]'
        ).text
        balance_old = 0 if wk == '---' else int(wk.replace(',', ''))
        logger.info(f'  -- 現在の残高: {balance_old} 円')
        return balance_old

    def pilot_depositing(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info('  入金処理開始')
        # ==============================
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
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='戻る'])[1]/following::span[1]").click()
        logger.debug('  SUBMIT depositing.')

    def pilot_logout(self):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("https://keiba.rakuten.co.jp/")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.glonavmain')))
        if self.is_element_present(By.ID, 'PRmodal'):
            logger.warn('  PRmodal 発見。閉じます。')
            # driver.find_element_by_css_selector('#PRmodal > div:nth-child(4)').click()
            driver.find_element_by_xpath('/html/body/section/div[2]/div').click()
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result

    def pilot(self):
        driver = self.driver
        wait = self.wait
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
                self.pilot_record.append(
                    f"{user['name']}: Already done today.  SKIP."
                )
                continue

            need_report += 1
            try:
                logger.info(' 楽天競馬にログイン')
                # ==============================
                balance_old = self.pilot_login(user)

                logger.info(' 入金処理')
                # ==============================
                self.pilot_depositing(user)

                logger.info(' 入金完了確認')
                # ==============================
                driver.find_element_by_link_text(u"投票画面へ").click()
                for i in range(5):
                    time.sleep(5)
                    driver.find_element_by_link_text(u"更新").click()
                    # driver.find_element_by_link_text(u"更新").click()
                    wk = driver.find_element_by_xpath(r'//*[@id="menuBar"]/div/div[2]/div/ul/li[2]/span[2]').text
                    logger.debug(f" -- 最新残高: RawValue=<{wk}> / RemoveComma=<{wk.replace(',','')}>")
                    balance_new = 0 if wk == '---' else int(wk.replace(',', ''))
                    logger.info(f"  {i}: {balance_old}->{balance_new}")
                    if balance_new > balance_old:
                        last_dones[who] = datetime.datetime.now()
                        self.last_done['Rkeiba'] = last_dones
                        logger.info(f" {who}: Complete at {last_dones[who].strftime('%c')}.")
                        self.pilot_record.append(f"{user['name']}: {balance_old}->{balance_new}")
                        break
            except (TimeoutException, NoSuchElementException) as e:
                self.pilot_record.append(f"{user['name']}: Ex={type(e)}")
                logger.error(e.args)
            except Exception as e:
                self.pilot_record.append(f"{user['name']}: Ex={type(e)} {e.args}")
                # self.pilot_record.append(f"{user['name']}: Unexpected error: {sys.exc_info()[0]}")
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
            # ==============================

        logger.info(f"実行記録を保存")
        # ==============================
        try:
            with open('last_done.yaml', 'w', encoding='utf-8') as f:
                logger.debug(f" -- {self.last_done['Rkeiba']}")
                yaml.dump(self.last_done,f,encoding=r'utf-8',allow_unicode=True)
                logger.info(f" 実施記録を保存しました")
        except:
            logger.info(f" 実施記録を保存できませんでした(ignore)")
        logger.info(f"全処理を完了")
        # ==============================
        driver.quit()
        logger.info(f" 処理結果: {self.pilot_record}, need_report: {need_report}")
        if need_report > 0 and self.pilot_record != []:
            self.reporter.report(f" 処理結果: {self.pilot_record}")
            logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

if __name__ == "__main__":
    App = Rkeiba()
    App.setup()
    App.pilot()
