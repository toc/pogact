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


class NanacoBalance(RPAbase.nanaco.Nanaco):

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            'NanacoBalance', 'Nanaco', __file__,
            '0.2', '$Rev$', 'Alpha'
        )
    
    def prepare(self, name=None, clevel=None, flevel=None):
        if name is None:
            name = self.appdict.name
        super().prepare(name)

    def pilot_setup(self):
        options = Options()
        if not __debug__:
            options.add_argument(r'--headless')
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
            wk = self.exception_message(e)
            logger.error(wk)
            result.append(wk)
        finally:
            self.pilot_result.append( [account['name'],result] )


if __name__ == "__main__":
    import pprint
    try:
        rpa = NanacoBalance()
        # 設定ファイル読み込み
        rpa.prepare('nanaco残高確認')
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
