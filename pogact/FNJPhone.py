#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from webdrivermanager import ChromeDriverManager
import yaml
import pandas as pd


class FNJPhone():
    """
    """
    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        # pass
        self.driver = None
        self.driverinfo = []
        self.wait = None
        self.config = {}
        self.pilot_param = {}
        self.pilot_result = []
        # form Katalon++
        self.accept_next_alert = True


    def prepare(self):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare work file/folder, and so on.
        """
        # pass
        try:
            with open(r'settings.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(e.args)
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
        # Driver
        dm = ChromeDriverManager()
        self.driverinfo = dm.download_and_install()
        # prameter
        now = datetime.datetime.now()
        diff = 62 if now.day <= 15 else 31
        target_day = now - datetime.timedelta(days=diff) 
        self.pilot_param['year'] = target_day.year
        self.pilot_param['month'] = target_day.month
        print(self.pilot_param)

    def setup(self):
        """
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        # ブラウザーを起動
        options = Options()
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(self.driverinfo[1], options=options)
        self.driver.implicitly_wait(10)
        # self.wait = Wait(self.driver,3)
   
    def login(self):
        """
        Log-in target web site.
        """
        config = self.config
        driver = self.driver

        driver.get("https://zeny.cyberhome.ne.jp/user/login.aspx")
        driver.find_element_by_id("LoginBody1_Tb_Account").click()
        driver.find_element_by_id("LoginBody1_Tb_Account").send_keys(config['id'])
        driver.find_element_by_id("LoginBody1_Tb_Passsword").click()
        driver.find_element_by_id("LoginBody1_Tb_Passsword").send_keys(config['pw'])
        driver.find_element_by_id("LoginBody1_Btn_Login").click()
        # pass
    
    def pilot(self):
        """
        Pilot automatically, to get your informations.
        """
        param = self.pilot_param
        driver = self.driver

        driver.find_element_by_link_text(u"取引内容の確認").click()
        driver.find_element_by_id("TransactionBody1_Ddl_Year").click()
        Select(driver.find_element_by_id("TransactionBody1_Ddl_Year")).select_by_visible_text(str(param['year']))
        driver.find_element_by_id("TransactionBody1_Ddl_Month").click()
        Select(driver.find_element_by_id("TransactionBody1_Ddl_Month")).select_by_visible_text(str(param['month']))
        driver.find_element_by_id("TransactionBody1_Ddl_Month").click()
        driver.find_element_by_id("TransactionBody1_Btn_Search").click()

        driver.save_screenshot(f"FNJPhone-{param['year']}{param['month']}.png")
        table = driver.find_element_by_xpath(r'//*[@id="TransactionBody1_PanelList"]/table[2]/tbody/tr/td/table')
        # with open(f"FNJPhone-{param['year']}{param['month']}.html", "w") as f:
        #     f.write(table.page_source)
        # //*[@id="TransactionBody1_PanelList"]/table[2]/tbody/tr/td/table/tbody/tr[1]
        # contents = []
        # for tr in table.find_elements_by_xpath(r'tbody/tr'):
        #     row = []
        #     tds = tr.find_elements_by_xpath(r'td')
        #     # print(tds)
        #     if tds == []:
        #         tds = tr.find_elements_by_xpath(r'th')
        #     for td in tds:
        #         row.append(td.text)
        #     contents.append(row)

        # print(contents)
        # obj = pd.Series(contents)
        ps = driver.page_source
        print(type(ps))
        print(ps[0:30])
        obj = pd.read_html(ps, match='サービス名')
        # obj = pd.read_html(unicode(ps, 'cp932').encode('utf-8') , match='サービス名')
        # obj = pd.read_html(ps.encode('cp932').decode('utf-8'), match='サービス名')
        with open(f"FNJPhone-tmp.html", 'w', encoding='utf-8') as fp:
            fp.write(ps)
        with open(f"FNJPhone-tmp.html", 'r', encoding='utf-8') as f:
            ps = f.read()
        obj = pd.read_html(ps, match='サービス名')
        print(len(obj))
        print(obj[4])
        self.pilot_result.append([f"{param['year']}{param['month']}", obj[4].to_csv()])
        with open(f"FNJPhone-{param['year']}{param['month']}.html", 'w', encoding='utf-8') as f:
            # idx = 0
            # for tab in obj:
            #     f.write(f"=={idx}==\n")
            #     f.write(f"{obj[idx]}\n\n")
            #     idx += 1
            f.write(
                self.config['html_string'].format(
                    css_string=self.config['css_string'],
                    table=obj[4].to_html(classes='mystyle'),
                )
            )
        # print(contents)

        # driver.close()

    def logout(self):
        """
        Log-out from web site.
        """
        # pass
        driver = self.driver

        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='田中俊明'])[1]/following::img[1]").click()


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        print(self.pilot_result)

if __name__ == "__main__":
    try:
        App = FNJPhone()
        App.prepare()
        App.setup()
        App.login()
        App.pilot()
        App.logout()
        App.tearDown()
    except Exception as e:
        print(e.args)
        if App:
            if App.driver:
                App.driver.quit()