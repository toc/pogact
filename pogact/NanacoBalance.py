# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import sys
import time
import re
import yaml
import RPAbase.nanaco
from logutils.AppDict import AppDict
import logutils.mailreporter

class NanacoBalance(RPAbase.nanaco.Nanaco):

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'NanacoBalance', # r'Nanaco_user', 
            __file__, r'0.1', r'$Rev$', r'Alpha'
        )
        self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', self.appdict.name)
    
    def prepare(self, name=None, clevel=None, flevel=None):
        if name is None:
            name = self.appdict.name
        super().prepare(name)   #, clevel=None, flevel=flevel)

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option(r'useAutomationExtension', False)
        options.add_experimental_option(r'excludeSwitches', ['enable-automation'])
        return super().pilot_setup(options)

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.critical(f'Reach pilot_internal!!')

        result = []
        try:
            # 残高情報を確認
            logger.info(f'  - 残高情報を確認')
            # driver.get("https://www.nanaco-net.jp/pc/emServlet")
            logger.debug(f'  wait for visibility_of_element_located: (By.ID,"memberTblMid")')
            wait.until(EC.visibility_of_element_located((By.ID,"memberTblMid")))
            #
            money_info = driver.find_element_by_id("memberInfoFull")
            detail_box = money_info.find_elements_by_class_name("detailBox")
            for detail in detail_box:
                # Title
                divs = detail.find_elements_by_xpath("div")
                wk = f'{divs[0].text.splitlines()[0]}'
                logger.debug(f'□{wk}')
                result.append(f'□{wk}')
                # nanaco balance (e-money)
                wk = f'{"/".join(divs[1].text.splitlines())}'
                logger.debug(f' -{wk}')
                result.append(f' -{wk}')
                # nanaco points (the points which will expire earlier)
                wk = divs[2].text.splitlines()
                wk2 = f'{"/".join(wk[0:2])}'
                logger.debug(f' -{wk2}')
                result.append(f' -{wk2}')
                wk2 = f'{"/".join(wk[3:5])}'
                logger.debug(f' --{wk2}')
                result.append(f' --{wk2}')
                # nanaco points (the points which will expire later)
                wk2 = f'{"/".join(wk[5:7])}'
                logger.debug(f' --{wk2}')
                result.append(f' --{wk2}')
        except Exception as e:
            wk = f' Caught Ex(raise upstream): it happens something wrong.: {type(e)} {e.args}'
            logger.error(wk)
            result.append(wk)
        finally:
            self.pilot_result.append( [account['name'],result] )


if __name__ == "__main__":
    try:
        from logging import WARNING, DEBUG
        import pprint
        App = NanacoBalance()
        App.prepare(clevel=WARNING)
        App.pilot()
        if App.pilot_result != []:
            App.reporter.report(
                pprint.pformat(App.pilot_result, width=72)
            )
            App.logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")

    except Exception as e:
        print(e.args)
        if App:
            if App.driver:
                App.driver.quit()
