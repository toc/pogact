# -*- coding: utf-8 -*-
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RBankBase import RBankBase
from logutils.AppDict import AppDict



class RBankCampaign(RBankBase):
    """
    """

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'RBankCampaign', 'RakutenBank', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        super().prepare('楽天銀行: キャンペーンエントリー')
        self.last_done[self.appdict.name] = self.last_done.get(self.appdict.name,{})
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return super().pilot_setup(options)

    def need_execute(self,account):
        """
        1日1回のみ実行する。
        ＝最終実行時刻が本日0時より以前の場合のみ実行する。
        """
        logger = self.logger
        appdict = self.appdict

        last_dones = self.last_done.get(appdict.name,{})
        result = True
        last_done = last_dones.get(account['name'],datetime.min)
        if appdict.data['today'] <= last_done:
            logger.warn(f' Already executed at [{last_done}].  EXIT !')
            result = False
        return result

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        logger.debug(f'  @@pilot_internal: START')
        appdict.data['log'] = []

        logger.info( f'  実行前チェック')
        # ==============================
        # execflag = True
        # if hasattr(self,'need_execute'):
        execflag = self.need_execute(account)
        if execflag is True:
            #
            logger.info( f'  キャンペーンページへ移動')
            # ==============================
            self.save_current_html('_0','html')
            # ------------------------------
            logger.debug( f'  - 商品･サービス一覧')
            po = (By.LINK_TEXT,'商品･サービス一覧')
            wait.until(EC.element_to_be_clickable(po))
            driver.find_element(*po).click()
            self.save_current_html('_1','html')
            # ------------------------------
            logger.debug( f'  - キャンペーン等')
            po = (By.LINK_TEXT,'キャンペーン等')
            wait.until(EC.element_to_be_clickable(po))
            driver.find_element(*po).click()
            self.save_current_html('_2','html')

            logger.info( f'  キャンペーン一覧を処理')
            # ==============================
            num_items_tried = 0
            max_items_tried = 3         # TODO: パラメータ化する
            while self.pilot_internal1():
                num_items_tried += 1
                if num_items_tried >= max_items_tried:
                    logger.info( f'  処理上限到達のためbreak')
                    break
            self.last_done[appdict.name][account['name']] = datetime.now()
            wk = f'  応募完了したリンク数[{num_items_tried}]'
            logger.info( wk)
            appdict.data['log'].insert(0,wk)
        else:
            #
            logger.info( f'  実行条件未成立')
            # ==============================
            appdict.data['log'].append("実行条件未成立: SKIP")
        #
        ###TODO: 実行ログのメール通知準備: Framework側に持っていきたい
        wk = {}
        wk[account['name']] = appdict.data['log']
        self.pilot_result.append(wk)
        #
        logger.debug(f'  @@pilot_internal: END')

    def pilot_internal1(self):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        logger.debug(f'  @@pilot_internal1: START')

        logger.debug(f'  - キャンペーン一覧を探索')
        # ==============================
        po = (By.XPATH,'/html/body/center[2]/table/tbody/tr/td/table/tbody/tr/td')
        wait.until(EC.visibility_of_element_located(po))
        tbl_td = driver.find_element(*po)
        po = (By.XPATH,'form')
        forms = tbl_td.find_elements(*po)
        logger.debug(f'  -- formを発見[{len(forms)}個]')
        # ------------------------------
        result = False
        logger.debug(f'  - 先頭から一定数を処理')
        for f in forms:
            id = f.get_attribute('id')
            logger.debug(f'  -- form[id={id}]を処理')
            if id == 'BREAD_LIST':
                logger.debug(f'  --- [id={id}]のためSKIP')
                continue
            # ------------------------------
            try:
                po = (By.XPATH,'table/tbody/tr/td[2]/div/div[1]/a')
                title_text = f.find_element(*po).text
                po = (By.XPATH,'table/tbody/tr/td[3]/div/a')
                a_elem = f.find_element(*po)
                script = a_elem.get_attribute('onclick')
                terms = script.split(',')
                logger.debug(f'  --- Onclick: >{terms[3:]}<')
                if len(terms) > 6 and terms[6] == "'true']]);":
                    # ------------------------------
                    logger.info( f'  ---- 応募:[{title_text}]')
                    a_elem.click()
                    po = (By.TAG_NAME,"body")
                    wait.until(EC.visibility_of_element_located(po))
                    # self.pilot_result.append(title_text)
                    appdict.data['log'].append(title_text)
                    result = True           # 応募完了
                    # ------------------------------
                    logger.info( f'  ---- 一覧に戻る')
                    po = (By.LINK_TEXT,"キャンペーン等一覧")
                    wait.until(EC.element_to_be_clickable(po))
                    driver.find_element(*po).click()
                    break
                else:
                    logger.info( f'  ---- SKIP:[{title_text}]')
                    continue
            except NoSuchElementException:
                logger.debug( f'  --- A_Link Not found.  Probably, All items have already done.  EXIT!!')
                break
        # True: １件応募完了で一覧を更新してリターン
        # False: 応募リンクのない広告が先頭にある or DIRECT応募可能な広告なしでループ完了
        logger.debug(f'  @@pilot_internal1: END')
        return result


if __name__ == "__main__":
    import pprint
    try:
        App = RBankCampaign()
        App.prepare()
        App.pilot('RakutenBank', 'RBankCampaign')
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exception_message(e)}')
        if App.driver:
            App.driver.quit()
    finally:
        # App.pilot_result.sort(key=itemgetter(0))
        result = App.pilot_result
        if result != []:
            import pprint
            App.report(
                pprint.pformat(result, width=40)
            )

# if __name__ == "__main__":
#     try:
#         from operator import itemgetter
#         App = RBankCampaign()
#         App.prepare()
#         App.pilot()
#         App.pilot_result.sort(key=itemgetter(0))
#         App.report(
#             pprint.pformat(App.pilot_result, width=40)
#         )
#         App.tearDown()
#     except Exception as e:
#         print(f'Caught Exception: {type(e)} {e.args if hasattr(e,"args") else str(e)}')
#         if App.driver is not None:
#             App.driver.quit()
