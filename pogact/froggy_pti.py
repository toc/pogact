# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
from RPAbase.Froggy import Froggy
from logutils.AppDict import AppDict

class Froggy_pti(Froggy):

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'froggy_pti', 'SMBCnikko_user', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.result = []

    def prepare(self):
        super().prepare('SMBC日興証券: Point投資')
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
            wk = f' Already executed at [{last_done}].  EXIT !'
            logger.warn(wk)
            self.result.append(wk)
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
            logger.info( f'  保有ｄポイント確認')
            # ==============================
            logger.debug(f'  - マイ資産で確認')
            url = "https://froggy.smbcnikko.co.jp/myasset/"
            driver.get(url)
            po = (By.XPATH,'//*[@id="__layout"]/div/main/div/div/div/section[2]/div/table/tbody/tr[2]')
            d_pt = driver.find_element(*po).text
            resmsg = f'pt infos:{d_pt}]'
            self.result.append(resmsg)
            #
            logger.info( f'  対象投信へ移動')
            # ==============================
            logger.debug(f'  - ファンド絞り込み')
            # fund_number = "1554"     # ETF
            # fund_number = "5020"     # ENEOS
            # fund_number = "8848"     # Leopalace
            fund_number = "9432"     # ＮＴＴ
            # fund_number = "8593"     # 三菱ＨＣＣ
            url = "https://froggy.smbcnikko.co.jp/stock/" + fund_number      # TODO:
            driver.get(url)
            po = (By.TAG_NAME,'body')
            logger.debug(f'  wait for {po}')
            wait.until(EC.visibility_of_element_located(po))
            self.save_current_html(stage_name('0'),'html')
            wk = self.appdict.wkfile(stage_name('_0'), "png")
            driver.save_screenshot(str(wk))
            # ------------------------------
            logger.debug(f'  - 購入ボタン押下')
            time.sleep(10)
            po = (By.CSS_SELECTOR,"#__layout > div > main > div > div > div > section > div.stockDetail__btn > button.btn--danger.btn--medium")
            driver.find_element(*po).click()
            po = (By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > header > h2")
            wait.until(EC.visibility_of_element_located(po))
            self.assertEqual(driver.find_element(*po).text, '買い注文')
            self.save_current_html(stage_name('1'),'html')
            # ------------------------------
            logger.debug(f'  - ｄポイント支払いを選択')
            pnt_before = driver.find_element(By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > div > div.orderForm > div:nth-child(1) > div > div > span").text
            po = (By.ID,"payment-type")
            # driver.find_element(*po).click()
            Select(driver.find_element(*po)).select_by_visible_text(u"保有dポイント")
            # invest_type = driver.find_element(*po).text
            # ------------------------------
            logger.debug(f'  - 購入額を指定')
            po = (By.XPATH,"//input[@type='tel']")
            driver.find_element(*po).clear()
            driver.find_element(*po).send_keys(account['amount'])
            # #
            # resmsg = f'pt usage: >{invest_type}<[{invest_fee}]'
            # self.result.append(resmsg)
            # ------------------------------
            logger.debug(f'  - 特定口座を指定')
            po = (By.ID,"account")
            driver.find_element(*po).click()
            Select(driver.find_element(*po)).select_by_visible_text(u"特定口座")
            # ------------------------------
            logger.debug(f'  - 注文実行')
            logger.debug(f'  -- 実行するボタン押下')
            wk = self.appdict.wkfile(stage_name('_1-order'), "png")
            driver.save_screenshot(str(wk))
            driver.find_element(By.XPATH,"//div[@id='__layout']/div/div/aside/div/div/div/div[2]/div[5]/button").click()
            logger.debug(f'  -- この内容で注文するボタン押下')
            # 画面展開待ち
            po = (By.XPATH, '//*[@id="__layout"]/div/div/aside/div/div/div/div[2]/div[3]/button[2]')
            wait.until(EC.visibility_of_element_located(po))
            wk = driver.find_element(*po).text
            logger.debug(f'  --- >{wk}<')
            self.assertEqual(wk, '修正する')
            # 情報収集
            # -- 購入ファンド
            po = (By.CSS_SELECTOR, '#__layout > div > div > aside > div > div > div > div.trade__stock > div.trade__stockTitle')
            investment = driver.find_element(*po).text
            resmsg = f'stock title: [{investment}]'
            po = (By.CSS_SELECTOR, '#__layout > div > div > aside > div > div > div > div.trade__stock > div.trade__stockSubTitle')
            investment = driver.find_element(*po).text
            resmsg += f'[{investment}]'
            self.result.append(resmsg)
            # -- 供出費用
            po = (By.XPATH, '//*[@id="__layout"]/div/div/aside/div/div/div/div[2]/table/tbody/tr[1]')
            investment = driver.find_element(*po).text
            resmsg = f'pt usage: [{investment}]'
            self.result.append(resmsg)
            #
            po = (By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > header > h2")
            wait.until(EC.visibility_of_element_located(po))
            wk = driver.find_element(*po).text
            logger.debug(f'  --- >{wk}<')
            self.assertEqual(wk, '注文内容の確認')
            po = (By.CSS_SELECTOR, '.passwordInput__input')
            driver.find_element(*po).clear()
            driver.find_element(*po).send_keys(account['pwd3'])      # TODO: 外部パラメータ化
            self.save_current_html(stage_name('2'),'html')
            wk = self.appdict.wkfile(stage_name('_2-order'), "png")
            driver.save_screenshot(str(wk))
            po = (By.XPATH,"//div[@id='__layout']/div/div/aside/div/div/div/div[2]/div[3]/button")
            driver.find_element(*po).click()
            # 画面展開待ち
            logger.debug(f'  -- 注文完了画面を確認')
            po = (By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > div > div > section > a")
            wait.until(EC.visibility_of_element_located(po))
            wk = driver.find_element(*po).text
            logger.debug(f'  --- >{wk}<')
            self.assertEqual(wk, 'マイ資産を見る')
            #
            po = (By.CSS_SELECTOR,"#__layout > div > div > aside > div > div > header > h2")
            wait.until(EC.visibility_of_element_located(po))
            wk = driver.find_element(*po).text
            logger.debug(f'  --- >{wk}<')
            self.assertEqual(wk, '注文完了')
            self.save_current_html(stage_name('3'),'html')
            wk = self.appdict.wkfile(stage_name('_3-order'), "png")
            driver.save_screenshot(str(wk))
            logger.info( f'  購入申請内容確認')
            # ==============================
            po = (By.LINK_TEXT,"注文約定一覧")
            driver.find_element(*po).click()
            self.save_current_html(stage_name('4'),'html')
            wk = self.appdict.wkfile(stage_name('_4'), "png")
            driver.save_screenshot(str(wk))
            logger.debug(f'  -- 実行記録')
            self.last_done[self.appdict.name][account['name']] = datetime.now()
        else:
            # すでに実行済み
            pass
        #
        logger.debug(f'  - 後片付け')
        # ==============================
        logger.debug(f'  -- 報告メール準備')
        wk = {}
        wk[account['name']] = self.result
        self.pilot_result.append(wk)
        #
        logger.debug(f'  @@pilot_internal: END')


if __name__ == "__main__":
    try:
        App = Froggy_pti()
        App.prepare()
        App.pilot('SMBCnikko_user', 'froggy_pti')
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exception_message(e)}')
        if App.driver:
            App.driver.save_screenshot(f'abort')
            App.driver.quit()
    finally:
        result = App.pilot_result
        if result != []:
            import pprint
            # result.sort(key=itemgetter(0))
            App.report(
                pprint.pformat(result, width=40)
            )
