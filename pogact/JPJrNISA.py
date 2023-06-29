#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import datetime
# import re
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
import yaml
from pathlib import Path
###
import RPAbase.JPBankBase
import logutils.AppDict
import logutils.mailreporter

class JPJrNISA(RPAbase.JPBankBase.JPBankBase):
    """
    Get settings and current status of Jr-NISA.
    """
    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            r'JPJrNISA', __file__,
            r'0.9', r'$Rev$', r'Alpha'
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
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return super().pilot_setup(options)


    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
    
        result_wk = []
        # 現金残高
        if self.is_element_present(By.LINK_TEXT, "ダイレクトトップ"):
            driver.find_element(By.LINK_TEXT,"ダイレクトトップ").click()
            logger.debug('  wait for (By.ID, "strMain")')
            wait.until(EC.visibility_of_element_located((By.ID, 'strMain')))
            # 本体の処理
            title = driver.find_element(By.CSS_SELECTOR,"#strMain > div:nth-child(3) > h2 > span").text
            balance = driver.find_element(By.CSS_SELECTOR,"#strMain > div:nth-child(3) > div > div.col.w55 > p").text
            wk = f'{title}/{balance}'
            logger.info(f' - {wk}')
            result_wk.append(f'{wk}')
        # # NISA口座へ送金するときは総合口座のみに絞っておく & OTP受信のためのGmailを準備
        # time.sleep(120)

        # 積立設定
        if self.is_element_present(By.LINK_TEXT, "投資信託"):
            driver.find_element(By.LINK_TEXT,"投資信託").click()

            # 注意喚起ページが挿入されていればスキップする
            time.sleep(0.5)
            po = (By.XPATH, '//*[@id="contents"]/div[1]/h2')
            if self.is_element_present(*po):
                wk = driver.find_element(*po).text
                if wk == '大切なお知らせ':
                    wk = f'"{wk}"をskipします'
                    logger.debug(f'    -- {wk}')
                    result_wk.append(f'  - {wk}')
                    po = (By.XPATH, '//*[@id="button"]')
                    driver.find_element(*po).click()

            if self.is_element_present(By.LINK_TEXT, "お申し込み内容の照会・変更"):
                driver.find_element(By.LINK_TEXT,"お申し込み内容の照会・変更").click()
                pageobj = (By.XPATH, '//*[@id="mainContents"]/form[1]/table')
                logger.debug(f'    wait for {pageobj}')
                wait.until(EC.visibility_of_element_located(pageobj))
                table = driver.find_element(*pageobj)
                trs = table.find_elements(By.XPATH, 'tbody/tr')
                trs_cnt = len(trs)
                i = 3                   # i=0,1,2はヘッダ定義のためスキップ
                while i < trs_cnt:
                    # １行目：ファンド名
                    title = trs[i].find_element(By.XPATH,'td[2]').text
                    # ２行目：積立日、金額
                    i += 1
                    duedate = trs[i].find_element(By.XPATH,'td[1]').text
                    payment = trs[i].find_element(By.XPATH,'td[2]').text
                    # ３行目：情報なし
                    i += 1
                    # 情報まとめ
                    wk = f'{duedate}/{payment}'
                    logger.info(f'   - {title}:{wk}')
                    result_wk.append(f'  - {title}')
                    result_wk.append(f'    - {wk}')
                    # 次行へうつりループ繰り返し
                    i += 1

                # 積立実績
                driver.find_element(By.LINK_TEXT,"運用損益照会").click()
                pageobj = (By.XPATH, '//*[@id="mainContents"]/form/table[2]')
                logger.debug(f'    wait for {pageobj}')
                wait.until(EC.visibility_of_element_located(pageobj))
                table = driver.find_element(*pageobj)
                trs = table.find_elements(By.XPATH, 'tbody/tr')
                trs_cnt = len(trs)
                # 運用トータル
                hyouka = trs[trs_cnt-1].find_element(By.XPATH,'td[4]').text
                sonneki = trs[trs_cnt-1].find_element(By.XPATH,'td[7]').text
                wk = f'運用状況: 評価額={hyouka}/損益={sonneki}'
                logger.info(f' - {wk}')
                result_wk.append(f'{wk}')
                # ファンド別
                i = 2                   # i=0,1はヘッダ定義のためスキップ
                while i < trs_cnt - 1:
                    # １行目：ファンド名
                    title = trs[i].find_element(By.XPATH,'td[2]').text
                    # ２行目：積立日、金額
                    i += 1
                    hyouka = trs[i].find_element(By.XPATH,'td[3]').text
                    sonneki = trs[i].find_element(By.XPATH,'td[6]').text
                    # 情報まとめ
                    wk = f'評価額={hyouka}/損益={sonneki}'
                    logger.info(f'   - {title}:{wk}')
                    result_wk.append(f'  - {title}')
                    result_wk.append(f'    - {wk}')
                    # 次行へうつりループ繰り返し
                    i += 1

            else:
                wk = f'投資信託契約なし／重要通知あり: SKIP'
                logger.debug(f'    {wk}')
                result_wk.append(f'  - {wk}')

        # まとめ
        self.pilot_result.append([f'{account["name"]}',result_wk])
        pass


if __name__ == "__main__":
    from operator import itemgetter
    from pprint import pformat
    try:
        App = JPJrNISA()
        App.prepare()
        App.pilot("JPBank","JPJrNISA")
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exception_message(e)}')
    finally:
        App.pilot_result.sort(key=itemgetter(0))
        result = App.pilot_result
        if result != []:
            App.report(
                pformat(result, width=40)
            )
