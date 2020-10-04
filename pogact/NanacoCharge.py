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

class NanacoCharge(RPAbase.nanaco.Nanaco):

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'NanacoCharge', # r'Nanaco_user', 
            __file__, r'0.1', r'$Rev$', r'Alpha'
        )
    
    def prepare(self, name=None, clevel=None, flevel=None):
        if name is None:
            name = self.appdict.name
        super().prepare(name)  #, clevel=None, flevel=flevel)
        options = Options()
        # options.add_argument(r'--headless')
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option(r'useAutomationExtension', False)
        options.add_experimental_option(r'excludeSwitches', ['enable-automation'])

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.debug(f'@@Reach pilot_internal!!')

        wk = account.get('charge_with',"0")
        adding = -99 if wk is None else int(wk)
        if adding > 30 or adding <= 0:
            # Illegal parameter.
            logger.warn(f' - Illegal params.  SKIP!  : charge_with=>{str(adding)}<')
            return

        try:
            # 残高情報を確認
            logger.info(f'  - 残高情報を確認')
            logger.debug(f'  wait for visibility_of_element_located: (By.ID,"memberInfoFull")')
            wait.until(EC.visibility_of_element_located((By.ID,"memberInfoFull")))
            money_info = driver.find_element_by_id("memberInfoFull")
            detail_box = money_info.find_elements_by_class_name("detailBox")
            for detail in detail_box:
                divs = detail.find_elements_by_xpath("div")
                logger.debug(f'  □{divs[0].text}')  # title
                logger.debug(f'  -- {"/".join(divs[1].text.splitlines())}')  # electric money
                logger.debug(f'  -- {"/".join(divs[2].text.splitlines())}')  # nanaco points
            # ----------------------
            logger.info(f'  - クレジット・パスワード入力')
            logger.debug(f'  wait for visibility_of_element_located: (By.LINK_TEXT,"nanacoクレジットチャージ...")')
            wait.until(EC.visibility_of_element_located((By.LINK_TEXT,"nanacoクレジットチャージ クレジットチャージやオートチャージの各種設定・変更手続きができます。")))
            driver.find_element_by_link_text(u"nanacoクレジットチャージ クレジットチャージやオートチャージの各種設定・変更手続きができます。").click()
            # ----------------------
            logger.info(f'  - チャージパスワード入力')
            logger.debug(f'  wait for visibility_of_element_located: (By.NAME,"CRDT_CHEG_PWD")')
            wait.until(EC.visibility_of_element_located((By.NAME,"CRDT_CHEG_PWD")))
            driver.find_element_by_name("CRDT_CHEG_PWD").clear()
            driver.find_element_by_name("CRDT_CHEG_PWD").send_keys(account['charge_pw'])
            driver.find_element_by_name("ACT_ACBS_do_CRDT_CHRG_PWD_AUTH").click()
            # ----------------------
            logger.info(f'  - 入金メニュー選択')
            logger.debug(f'  wait for visibility_of_element_located: (By.LINK_TEXT,"クレジットチャージ（入金）")')
            wait.until(EC.visibility_of_element_located((By.LINK_TEXT,"クレジットチャージ（入金）")))
            driver.find_element_by_link_text(u"クレジットチャージ（入金）").click()
            # self.save_current_html('after_entering_credit_charge.html')
            # ----------------------
            # time.sleep(30)
            logger.info(f'  - 入金額選択(30000円)')
            logger.debug(f'  wait for visibility_of_element_located: (By.NAME,"INPUT_AMT")')
            wait.until(EC.visibility_of_element_located((By.NAME,"INPUT_AMT")))
            driver.find_element_by_name("INPUT_AMT").clear()
            driver.find_element_by_name("INPUT_AMT").send_keys(account['charge_with'])
            driver.find_element_by_name("ACT_ACBS_do_CRDT_CHRG_INPUT").click()
            # self.save_current_html('after_entering_charge_selection.html')
            # ----------------------
            logger.info(f'  - 申込みボタン（最終確認）')
            logger.debug(f'  wait for visibility_of_element_located: (By.NAME,"ACT_ACBS_do_CRDT_CHRG_CONF")')
            wait.until(EC.visibility_of_element_located((By.NAME,"ACT_ACBS_do_CRDT_CHRG_CONF")))
            msg = driver.find_element_by_id(r"formTbl").text
            logger.info(f'  -- 入金予定: {msg}')
            # self.save_current_html('before_last_confirm.html')
            logger.debug(f'  -- 申込ボタン押下')
            driver.find_element_by_name("ACT_ACBS_do_CRDT_CHRG_CONF").click()
            # 結果確認
            ### TODO
            print(u"結果確認は未実装！")
            # self.save_current_html('after_last_confirm.html')
        except Exception as e:
            logger.error(f' Caught Ex(raise upstream): it happens something wrong.: {type(e)} {e.args}')
            # self.save_current_html('00caught_exception.html')
            if self.is_element_present(By.ID, r'textSystem'):
                wk = driver.find_element_by_id(r'textSystem').text
                error_text = ','.join(wk.split('\n'))
                self.pilot_result.append(error_text)
                logger.error(f' !! {error_text}')
            raise(e)


if __name__ == "__main__":
    try:
        from logging import WARNING, DEBUG
        import pprint
        App = NanacoCharge()
        App.prepare(clevel=WARNING)
        App.pilot()
        pprint.pprint(App.pilot_result, width=80, compact=True)
        App.tearDown()
    except Exception as e:
        print(e.args)
        if App:
            if App.driver:
                App.driver.quit()
