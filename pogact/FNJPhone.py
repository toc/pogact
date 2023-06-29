#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import yaml
import pandas as pd
import logutils.AppDict
import RPAbase.FNJbase

class FNJPhone(RPAbase.FNJbase.FNJbase):
    """
    Get invoice from FNJ IP-Phone.
    """
    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'FNJPhone', 'FNJ', __file__,
            '0.2', '$Rev$', 'Alpha'
        )


    def prepare(self, name=None, clevel=None, flevel=None):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare work file/folder, and so on.
        """
        super().prepare(self.appdict.name)
        self.today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        self.logger.debug(f"{self.today.strftime('%c')}")
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

        if self.config.get('html_string') is None:
            self.config['html_string'] = '''
<html>
  <head>
  <meta charset="UTF-8" />
  <title>J2 Ranking</title>
  <style>{css_string}</style>
  </head>
  <body>
    {table}
  </body>
</html>
'''
        if self.config.get('css_string') is None:
            self.config['css_string'] = '''
<!--
.mystyle {
    font-size: 11pt;
    font-family: Arial;
    border-collapse: collapse;
    border: 1px solid silver;
}
.mystyle td, th {
    padding: 5px;
}
.mystyle tr:hover {
    background: silver;
    cursor: pointer;
}
-->
'''
        now = datetime.datetime.now()
        diff = relativedelta(months=2) if now.day <= 15 else relativedelta(months=1)
        target_day = now - diff 
        self.logger.debug(f'  - taget: {target_day.year}/{target_day.month}')
        self.pilot_param['year'] = target_day.year
        self.pilot_param['month'] = target_day.month


    def pilot_setup(self):
        """
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        options = Options()
        if not __debug__:
            options.add_argument(r'--headless')
        # イメージボタンが多用されているため、img表示は必要
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return super().pilot_setup(options)


    def pilot(self):
        """
        Pilot automatically, to get your informations.
        """
        driver, wait = self.pilot_setup()
        logger = self.logger
        param = self.pilot_param

        yyyymm = format(param['year'], '04d') + format(param['month'], '02d')

        need_report = 0

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users = self.config.get('users',{})
        users_rakuten = users.get('FNJ',[])
        # Get service information
        svcs = self.config.get('services',{})
        svcs_rkeiba = svcs.get('FNJPhone',[])
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
            # パスワード, pin 以外をデバッグログに出力
            wk = {k:v for (k,v) in user.items() if k in ('name','id')}
            logger.debug(f"  params: {wk}")
            # 実行記録を確認：当日中の実行は１回に限定したい
            who = user['id']
            last_dones = self.last_done.get('FNJPhone',{})
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
                logger.info(' FNJ(zeny)にログイン')
                # ==============================
                if self.pilot_login(user):
                    logger.debug(' 取引ページに移動')
                    # ------------------------------
                    driver.find_element(By.LINK_TEXT,u"取引内容の確認").click()

                    logger.debug(' 年月を指定')
                    # ------------------------------
                    driver.find_element(By.ID,"TransactionBody1_Ddl_Year").click()
                    Select(driver.find_element(By.ID,"TransactionBody1_Ddl_Year")).select_by_visible_text(str(param['year']))
                    driver.find_element(By.ID,"TransactionBody1_Ddl_Month").click()
                    Select(driver.find_element(By.ID,"TransactionBody1_Ddl_Month")).select_by_visible_text(str(param['month']))
                    driver.find_element(By.ID,"TransactionBody1_Ddl_Month").click()
                    driver.find_element(By.ID,"TransactionBody1_Btn_Search").click()

                    logger.debug(' ハードコピーを採取')
                    # ------------------------------
                    wk = str(self.appdict.wkfile(f"-{yyyymm}", "png"))
                    driver.save_screenshot(wk)
                    table = driver.find_element(By.XPATH,r'//*[@id="TransactionBody1_PanelList"]/table[2]/tbody/tr/td/table')

                    logger.debug(' 請求項部分をhtmlで切り出して保存')
                    # ------------------------------
                    ps = driver.page_source
                    wk = str(self.appdict.wkfile(f"-tmp", "html"))
                    logger.debug(' -- Webソースをutf-8に揃えて解析する(tmpファイルを使用)')
                    with open(wk, 'w', encoding='utf-8') as fp:
                        fp.write(ps)
                    with open(wk, 'r', encoding='utf-8') as f:
                        ps = f.read()
                    obj = pd.read_html(ps, match='サービス名')
                    logger.debug(f'  numObj: {len(obj)}, obj[4]={obj[4]} ')
                    self.pilot_result.append([f"{param['year']}{param['month']}", obj[4].to_csv()])
                    wk = str(self.appdict.wkfile(f"-{yyyymm}", "html"))
                    with open(wk, 'w', encoding='utf-8') as f:
                        f.write(
                            self.config['html_string'].format(
                                css_string=self.config['css_string'],
                                table=obj[4].to_html(classes='mystyle'),
                            )
                        )
                    logger.debug(' 請求項部分をhtmlで切り出して保存')
                    # ------------------------------
                    last_dones[who] = datetime.datetime.now()
                    self.last_done['FNJPhone'] = last_dones
                    logger.info(f" {who}: Complete at {last_dones[who].strftime('%c')}.")

                else:
                    logger.error(f'  ログイン失敗！')

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
        rpa = FNJPhone()
        # 設定ファイル読み込み
        rpa.prepare('FNJPhoneの請求額確認')
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
