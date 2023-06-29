from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from datetime import datetime
import unittest, time, re
import RPAbase.RPAbase
from RPAbase.RakutenBase import RakutenBase
from logutils.AppDict import AppDict


class RakutenLottery(RakutenBase):
    """
    """

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'RakutenLottery', 'Rakuten', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        super().prepare('楽天くじ: エントリー')
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

    def pilot_internal1(self):
        """
        対象くじ一覧を返す
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        target_table = [
            # CSS_SELECTOR
            'body > div.luckykuji_wrapper > main > section.kuji_list',
            'body > div.luckykuji_wrapper > main > section.luckykuji_attention',
        ]
        result = []
        regex = re.compile('(\S+?)$')
        driver.get("https://kuji.rakuten.co.jp/")
        for targ in target_table:
            po = (By.CSS_SELECTOR, targ + ' > ul > li > a')
            links = driver.find_elements(*po)
            for link in links:
                entry = {}
                entry['url'] = link.get_attribute('href')
                logger.debug(f'  --url: {entry["url"]}')
                wk = re.search(regex,link.text)
                entry['name'] = wk.group(1)
                logger.debug(f'  --name: {entry["name"]}')
                result.append(entry)
        return result


    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        logger.debug(f'  @@pilot_internal: START')
        appdict.data['log'] = []

        url_list = self.pilot_internal1()

        for page in tqdm(url_list):
                try:
                    if page['url'] == 'https://pointmall.rakuten.co.jp/':
                        driver.get(page['url'])
                        time.sleep(1)
                        driver.find_element(By.XPATH,'//*[@id="side"]/div[1]/ul/li/div[1]/a/img').click()
                        driver.find_element(By.XPATH,'//*[@id="side"]/div[1]/ul/li/div[2]/div/div[1]/div[6]').click()
                        time.sleep(14)

                    elif page['url'] == 'https://point.rakuten.co.jp/doc/lottery/lucky/':
                        driver.get(page['url'])
                        time.sleep(2)
                        driver.find_element(By.XPATH,'//*[@id="cp_btn_start"]/a/img').click()
                        time.sleep(14)

                    else:
                        driver.get(page['url'])
                        time.sleep(1)
                        driver.find_element(By.XPATH,'//*[@id="entry"]').click()
                        time.sleep(14)

                except (NoSuchElementException, ElementNotInteractableException):
                    print('###エラー 次のくじに進みます。' + page['name'] + '###')
                    time.sleep(1)


        # logger.info( f'  実行前チェック')
        # # ==============================
        # # execflag = True
        # # if hasattr(self,'need_execute'):
        # execflag = self.need_execute(account)
        # if execflag is True:
        #     #
        #     logger.info( f'  キャンペーンページへ移動')
        #     # ==============================
        #     self.save_current_html('_0','html')
        #     # ------------------------------
        #     logger.debug( f'  - 商品･サービス一覧')
        #     po = (By.LINK_TEXT,'商品･サービス一覧')
        #     wait.until(EC.element_to_be_clickable(po))
        #     driver.find_element(*po).click()
        #     self.save_current_html('_1','html')
        #     # ------------------------------
        #     logger.debug( f'  - キャンペーン等')
        #     po = (By.LINK_TEXT,'キャンペーン等')
        #     wait.until(EC.element_to_be_clickable(po))
        #     driver.find_element(*po).click()
        #     self.save_current_html('_2','html')

        #     logger.info( f'  キャンペーン一覧を処理')
        #     # ==============================
        #     num_items_tried = 0
        #     max_items_tried = 3         # TODO: パラメータ化する
        #     while self.pilot_internal1():
        #         num_items_tried += 1
        #         if num_items_tried >= max_items_tried:
        #             logger.info( f'  処理上限到達のためbreak')
        #             break
        #     self.last_done[appdict.name][account['name']] = datetime.now()
        #     wk = f'  応募完了したリンク数[{num_items_tried}]'
        #     logger.info( wk)
        #     appdict.data['log'].insert(0,wk)
        # else:
        #     #
        #     logger.info( f'  実行条件未成立')
        #     # ==============================
        #     appdict.data['log'].append("実行条件未成立: SKIP")
        # #
        ###TODO: 実行ログのメール通知準備: Framework側に持っていきたい
        wk = {}
        wk[account['name']] = appdict.data['log']
        self.pilot_result.append(wk)
        #
        logger.debug(f'  @@pilot_internal: END')



if __name__ == "__main__":
    import pprint
    try:
        App = RakutenLottery()
        App.prepare()
        App.pilot('Rakuten', 'RakutenLottery')
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

