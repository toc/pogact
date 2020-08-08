#! /usr/bin/env python
# -*- coding: utf-8 -*-
# import sys
import time
# import re
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
# from webdrivermanager import ChromeDriverManager
import yaml
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
# import pandas as pd
import RPAbase.MineoBase
import logutils.AppDict
import logutils.mailreporter

class MineoPhone(RPAbase.MineoBase.MineoBase):
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
            r'MineoPhone', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', self.appdict.name)


    def prepare(self):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare work file/folder, and so on.
        """
        appdict = self.appdict
        super().prepare(appdict.name)
        self.today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        self.logger.debug(f"{self.today.strftime('%c')}")

        dldir = Path(__file__).with_name('pdfdownload')
        dldir.mkdir(exist_ok=True)  # 存在していてもOKとする（エラーで止めない）
        appdict.data['download_dir'] = str(dldir.resolve())  # absolute path.

        self.logger.info(f"@@@Start {appdict.name}({appdict.version_string()})")

    def pilot_setup(self):
        """
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        appdict = self.appdict
        options = Options()
        # options.add_argument(r'--headless')
        # イメージボタンが多用されているため、img表示は必要
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # PDF保存準備
        options.add_experimental_option("prefs", {
            "download.default_directory": appdict.data['download_dir'],
            "plugins.always_open_pdf_externally": True
        })

        return super().pilot_setup(options)

    def pilot(self):
        """
        Pilot automatically, to get your informations.
        """
        driver, wait = self.pilot_setup()
        logger = self.logger
        appdict = self.appdict

        need_report = 0

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users = self.config.get('users',{})
        users_rakuten = users.get('Mineo',[])
        # Get service information
        svcs = self.config.get('services',{})
        svcs_rkeiba = svcs.get(appdict.name,[])
        if len(users_rakuten) * len(svcs_rkeiba) == 0:
            logger.warn(f"No user({len(users_rakuten)}) or service({len(svcs_rkeiba)}) is found.  exit.")
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
            last_dones = self.last_done.get(appdict.name,{})
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
                logger.info(' mineo mypage にログイン')
                # ==============================
                if self.pilot_login(user):
                    logger.debug(' ご利用料金ページに移動')
                    # ------------------------------
                    # driver.find_element_by_link_text(u"ご利用料金").click()
                    driver.get("https://mypage.eonet.jp/Bill/details")

                    logger.debug(' 年月を指定')
                    # ------------------------------
                    logger.debug(f'  - wait for visibility_of_element_located((By.ID,"billingYm"))')
                    wait.until(EC.visibility_of_element_located((By.ID,"billingYm")))

                    now = datetime.datetime.now()
                    diff = relativedelta(months=2) if now.day <= 15 else relativedelta(months=1)
                    target_day = now - diff 
                    select_item = f'{format(target_day.year, "04d")}年{format(target_day.month, "02d")}月ご利用分'
                    logger.debug(f'  - taget: {select_item}')
                    driver.find_element_by_id("billingYm").click()
                    Select(driver.find_element_by_id("billingYm")).select_by_visible_text(select_item)

                    logger.debug(f'  - wait for visibility_of_element_located((By.ID,"pdfDownload"))')
                    wait.until(EC.element_to_be_clickable((By.ID,"pdfDownload")))
                    driver.find_element_by_id("pdfDownload").click()
                    time.sleep(8)           # ダウンロード完了待ち

                    logger.debug(' 実行記録情報を更新')
                    # ------------------------------
                    last_dones[who] = datetime.datetime.now()
                    self.last_done[appdict.name] = last_dones
                    logger.info(f" {who}: Complete at {last_dones[who].strftime('%c')}.")

                else:
                    logger.error(f'  ログイン失敗！')

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
                self.pilot_logout()

            logger.info(f"処理完了: user={user['name']}")

        # logger.info(f"全処理を完了")
        # # ==============================
        # self.tearDown()
        
        logger.info(f" 処理結果: {self.pilot_result}, need_report: {need_report}")
        if need_report > 0 and self.pilot_result != []:
            self.reporter.report(f" 処理結果: {self.pilot_result}")
            logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")


if __name__ == "__main__":
    try:
        App = MineoPhone()
        App.prepare()
        App.pilot()
        App.tearDown()
    except Exception as e:
        print(e.args)
        if App:
            if App.driver:
                App.driver.quit()