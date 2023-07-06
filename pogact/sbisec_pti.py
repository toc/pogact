# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from RPAbase.SBISec import SBISec
from logutils.AppDict import AppDict


class SBISecReport(SBISec):

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'SBISec_invest_by_point', 'SBI_user', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.result = []

    def prepare(self):
        super().prepare('SBI証券: Point投資')
        # create new entry, if not exists.
        self.last_done[self.appdict.name] = self.last_done.get(self.appdict.name,{})
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return super().pilot_setup(options)

    def need_execute(self,account):
        """
        1週1回のみ実行する。
        ＝西暦年(yyyy)と週番号(week No)が前回実行時と異なっていたら実行する。
        ※日本基準（月曜始まり）で算出。
        See: https://dev.classmethod.jp/articles/python_week_numbers/
        """
        logger = self.logger
        appdict = self.appdict

        last_dones = self.last_done.get(appdict.name,{})
        result = True
        last_done = last_dones.get(account['name'],datetime.min)
        wk = last_done.isocalendar()
        ld_weeknum = wk[0] * 100 + wk[1]         # yyyy * 10 + week_number(1-53)
        wk = appdict.data['today'].isocalendar()
        now_weeknum = wk[0] * 100 + wk[1]
        logger.debug(f'  Compare weeknum: curr[{now_weeknum}] vs prev[{ld_weeknum}]')
        if now_weeknum <= ld_weeknum:
            # 現在月が最終実行月以前であれば実行不要
            resmsg = f' Already done for [{ld_weeknum}] at [{last_done}].  EXIT !'
            logger.warn(resmsg)
            self.result.append(resmsg)
            result = False
        return result

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        stage_name = lambda x: f'_{str(self.appdict.data["today"].date())}_{account["name"]}_{x}'

        logger.info( f'  実行前チェック')
        # ==============================
        execflag = self.need_execute(account)
        if execflag is True:
            #
            logger.info( f'  投信へ移動')
            # ==============================
            driver.get("https://site1.sbisec.co.jp/ETGate/")
            po = (By.TAG_NAME,'body')
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            y = stage_name('_test')
            self.save_current_html('0','html')
            # ------------------------------
            po = (By.XPATH,"//img[@alt='投信・外貨建MMF']")
            driver.find_element(*po).click()
            #
            logger.info( f'  ファンド検索')
            # ==============================
            logger.debug(f'  - ファンド絞り込み')
            po = (By.ID,'fundSearch')
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            self.save_current_html('1','html')
            driver.find_element(*po).clear()
            driver.find_element(*po).send_keys(u"ＳＢＩ・V")
            po = (By.NAME,'ACT_clickToSearchFund')
            driver.find_element(*po).click()
            logger.debug(f'  - ファンド詳細画面へ遷移')
            po = (By.ID,account['fund'])          #TODO:
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            fund = driver.find_element(*po)
            fundname = fund.text
            resmsg = f'fund: >{fund.text}<'
            self.result.append(resmsg)
            fund.click()
            #
            logger.info( f'  購入手続き')   
            # ==============================
            po = (By.LINK_TEXT,'金額買付')          #TODO:
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            self.save_current_html('2','html')
            driver.find_element(*po).click()
            # ------------------------------
            po = (By.NAME,'payment')          #TODO:
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            self.save_current_html('3','html')
            amount_of_invest = account['amount']                  # TODO:
            payment = driver.find_element(*po)
            payment.clear()
            payment.send_keys(str(amount_of_invest))
            #
            po = (By.XPATH,'//*[@id="MAINAREA02_780"]/form/table[2]/tbody/tr[3]/td/table/tbody/tr[1]')          #TODO:
            pnt_before = driver.find_element(*po).text
            #
            po = (By.ID,'zenbushiyou')          #TODO:
            # po = (By.ID,'riyoushinai')          #TODO:
            driver.find_element(*po).click()
            #
            po = (By.ID,'pwd3')          #TODO:
            deal_pw = driver.find_element(*po)
            deal_pw.clear()
            deal_pw.send_keys(account['pwd3'])
            #
            po = (By.XPATH,"//img[@alt='注文確認画面へ']")          #TODO:
            driver.find_element(*po).click()
            #
            logger.info( f'  購入申請内容確認')
            # ==============================
            #TODO:
            self.save_current_html(stage_name('4'),'html')
            # result = self.assertEqual(result_msg,'以下の内容でエントリーを受け付けました。')
            wk = self.appdict.wkfile(stage_name('_4-order'), "png")
            driver.save_screenshot(str(wk))
            # ------------------------------
            #TODO:
            po = (By.XPATH,"//img[@alt='注文発注']")          #TODO:
            driver.find_element(*po).click()
            # -- 発注情報収集
            # po = (By.XPATH,'//*[@id="MAINAREA02_780"]/form/div[4]/table/tbody/tr[4]')
            # resmsg = f'fund: >{driver.find_element(*po).text}<'
            # self.result.append(resmsg)
            # po = (By.XPATH,'//*[@id="MAINAREA02_780"]/form/div[4]/table/tbody/tr[6]')
            # resmsg = f'fund: >{driver.fullscreen_window(*po).text}<'
            # self.result.append(resmsg)
            # po = (By.XPATH,'//*[@id="MAINAREA02_780"]/form/div[4]/table/tbody/tr[7]')
            # resmsg = f'fund: >{driver.find_element(*po).text}<'
            # self.result.append(resmsg)
            #
            self.save_current_html(stage_name('5'),'html')
            wk = self.appdict.wkfile(stage_name('5-order'), "png")
            driver.save_screenshot(str(wk))
            logger.debug(f'  -- 実行記録')
            self.last_done[self.appdict.name][account['name']] = datetime.now()
            wk = {}
            wk[account['name']] = [
                {'fundname', fundname},
                {'Points before', pnt_before},
                {'amount of invest', amount_of_invest}
            ]
            self.pilot_result.append(wk)
        else:
            # すでに実行済み
            pass
        #
        logger.debug(f'  - 後片付け')
        # ==============================
        logger.debug(f'  -- 報告メール準備')
        #
        logger.debug(f'  @@pilot_internal: END')


if __name__ == "__main__":
    try:
        App = SBISecReport()
        App.prepare()
        App.pilot('SBI_user', 'SBISec_invest_by_point')
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exception_message(e)}')
        if App.driver:
            App.driver.quit()
    finally:
        result = App.pilot_result
        if result != []:
            import pprint
            # result.sort(key=itemgetter(0))
            App.report(
                pprint.pformat(result, width=40)
            )
