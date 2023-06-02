# -*- coding: utf-8 -*-
import time
import datetime
import yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from logging import DEBUG, INFO    # , WARNING, ERROR, CRITICAL
import logutils.AppDict
from RPAbase.RkeibaBase import RkeibaBase


class Rkeiba(RkeibaBase):
    """
    """
    def __init__(self):
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'Rkeiba', 'Rakuten', __file__,
            '0.2', '$Rev$', 'Alpha'
        )


    def prepare(self, name=None, clevel=None, flevel=None):
        super().prepare(self.appdict.name)
        self.today = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        self.logger.debug(f"{self.today.strftime('%c')}")
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")


    def pilot_setup(self):
        options = Options()
        if not __debug__:
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
        driver.find_element(By.LINK_TEXT,u"入金").click()
        # ポップアップに移動
        logger.debug('  wait for NEW POPUP WINDOW.')
        wait.until(lambda d: len(d.window_handles) > 1)
        logger.debug('  switch to NEW POPUP WINDOW.')
        driver.switch_to.window(driver.window_handles[1])
        #
        logger.info('  入金額指定')
        # ==============================
        po = (By.CSS_SELECTOR, "#depositNumberInput")
        logger.debug(f'  wait for {po}')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).click()
        driver.find_element(*po).clear()
        amount = int(user['charge']/100)
        logger.debug(f'  amount: >{str(amount)}<')
        driver.find_element(*po).send_keys(str(amount))
        po = (By.XPATH, '//*[@id="app"]/div/section/div[2]/section/section/form/div[3]/div/button')
        driver.find_element(*po).click()
        #
        logger.info('  入金指定確認＆実行！')
        # ==============================
        po = (By.CSS_SELECTOR, "#pinInput")
        logger.debug(f'  wait for {po}')
        wait.until(EC.visibility_of_element_located(po))
        driver.find_element(*po).click()
        driver.find_element(*po).clear()
        driver.find_element(*po).send_keys(user['pin'])
        po = (By.XPATH, '//*[@id="app"]/div/section/div[2]/section/section/form/div[3]/div/button')
        driver.find_element(*po).click()
        logger.debug('  SUBMIT depositing.')


    def check_balance(self):
        """
        Check current balance and return it as integer.
        This function assumes that top page of Rakuten keiba was already loaded.
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug(f'  @@START check balance')
        
        for i in range(8):
            logger.debug(f'  - {i}: wait.until(EC.visibility_of_element_located((By.LINK_TEXT,"更新")))')
            wait.until(EC.visibility_of_element_located((By.LINK_TEXT,'更新'))).click()
            wk = driver.find_element(By.XPATH,'//*[@id="balanceStatus"]/ul/li[3]/span/span[2]').text
            logger.debug(f'  - current balance: >{wk}<')
            if wk != '':
                break
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
            # 金額未指定ならデフォルト値(100円), 月あたりの最大実行回数(default:4)
            user['charge'] = user.get('charge', 100)
            user['max_per_month'] = user.get('max_per_month', 4)
            # パスワード, pin 以外をデバッグログに出力
            wk = {k:v for (k,v) in user.items() if k in ('name','id')}
            logger.debug(f"  params: {wk}")
            # 実行記録を確認：当日中の実行は１回に限定したい
            who = user['id']
            last_dones = self.last_done.get('Rkeiba',{})
            whos_done = last_dones.get(who)
            if type(whos_done) is not dict: whos_done = {}
            last_done = whos_done.get('last_done', datetime.datetime.min)
            logger.debug(f" {who}: today={self.today} vs last={last_done}")
            # 当日中の実行記録あり
            if self.today < last_done:
                logger.info(f" {who}: Already done today.  SKIP.")
                self.pilot_result.append(
                    f"{user['name']}: Already done today.  SKIP."
                )
                continue
            # 当月中の実行回数が規定値未満か
            this_month = self.today.replace(day=1)
            exec_month = whos_done.get('exec_month', datetime.datetime.min)
            exec_count = whos_done.get('exec_count', 0)
            if this_month > exec_month:
                # 月替わりを検出
                logger.info(f" Exec_count[{exec_count}] is reset becuse new month arrived. new=>{exec_month}<, old=>{this_month}<")
                exec_month = this_month
                exec_count = 0
            if exec_count >= user['max_per_month']:
                # 月あたりの最大実行回数を超過
                logger.debug(f" SKIP execution because exec_count[{exec_count}] exceeds limitation[{user['max_per_month']}].")
                continue

            need_report += 1
            try:
                logger.info(' 楽天競馬にログイン')
                # ==============================
                if self.pilot_login(user):
                    # login succeed.
                    driver.get('https://my.keiba.rakuten.co.jp/')
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
                            whos_done['exec_month'] = exec_month
                            whos_done['exec_count'] = exec_count + 1
                            whos_done['last_done'] = datetime.datetime.now()
                            last_dones[who] = whos_done
                            self.last_done['Rkeiba'] = last_dones
                            logger.info(f" {who}: Complete at {whos_done['last_done'].strftime('%c')}.")
                            result_msg = f"{user['name']}: {balance_old}->{balance_new}, {whos_done['exec_count']}@{whos_done['exec_month'].strftime('%Y-%m')}."
                            break
                    self.pilot_result.append(result_msg)
                else:
                    # login failed
                    pass

            except (TimeoutException, NoSuchElementException) as e:
                self.pilot_result.append(f"{user['name']}: Ex={self.exception_message(e)}")
                logger.error(e.args)
            except Exception as e:
                self.pilot_result.append(f"{user['name']}: Ex={self.exception_message(e)}")
                # self.pilot_result.append(f"{user['name']}: Unexpected error: {sys.exc_info()[0]}")
                logger.critical(f"Exception: {self.exception_message(e)}")
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
        logger.info(f" 処理結果: {self.pilot_result}, need_report: {need_report}")
        if need_report == 0:
            self.pilot_result = []


if __name__ == "__main__":
    import pprint
    try:
        rpa = Rkeiba()
        # 設定ファイル読み込み
        rpa.prepare('楽天競馬')
        # ブラウザ操作
        # -- Webdriverの準備からquitまで実施する
        rpa.pilot()
        # ブラウザの後始末
        rpa.tearDown()
    except Exception as e:
        rpa.pilot_result.insert(0,rpa.exception_message(e))
    finally:
        # 結果をメール送信する(ブラウザは終了済み)
        result = rpa.pilot_result
        if len(result) > 0:
            rpa.report(
                pprint.pformat(result, width=45)
            )
            pprint.pprint(result, width=45)
