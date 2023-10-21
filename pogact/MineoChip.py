# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
import time, re
import yaml
import logutils.AppDict
import RPAbase.MineoKingBase

class MineoChip(RPAbase.MineoKingBase.MineoKingBase):
    """
    Mineoチップを贈るツール
    - TODO: チップ送信のためのURLはハードコートしています。（＝送信相手選択をサボってる）
    - TODO: ReCapthaをかいくぐれて「いない」バージョン

    贈るチップ数は settingsu.yaml に定義できるようになりました。

    実行時、ReCapthaに捕まったらパスワード入力・画像選択をソッコーで行い
    ログインボタンを押してください。
    """
    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'MineoKing', 'MineoChip', __file__,
            '0.1', '$Rev$', 'Alpha'
        )


    def prepare(self, name=None, clevel=None, flevel=None):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare work file/folder, and so on.
        """
        super().prepare(self.appdict.name)
        try:
            #TODO: last_done.yamlで手当できないか？
            fname = str(self.appdict.name).lower()
            with open(f'{fname}_remain.yaml', 'r', encoding='utf-8') as f:
                self.appdict.data['ptlinks'] = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f' Caught Ex(Ignore): Reviving previous remain list: {self.exception_message(e)}')
            self.appdict.data['ptlinks'] = {}


    def pilot_setup(self):
        """
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        options = Options()
        # Headlessモードでの実行不可
        # if not __debug__:
        #     options.add_argument(r'--headless')
        # イメージボタンが多用されているため、img表示は必要
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        driver, wait = super().pilot_setup(options)

        return [driver,wait]

    def pilot_internal2(self):
        """
        ファンのページが開いている前提で残りチップ数を確認
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        #
        logger.debug('@@pilot_internal2:START')
        # 贈るボタン押下
        try:
            driver.get("https://king.mineo.jp/my/6fc123075f274c10")
            po = (By.PARTIAL_LINK_TEXT,"10MBチップを贈る")
            logger.debug(f'  -- wait until: {po}')
            wait.until(EC.visibility_of_element_located(po))
            driver.find_element(*po).click()
            # ダイアログ対応
            po = (By.CSS_SELECTOR,"body > div.blockUI.blockMsg.blockPage > div > div.card-body > p")
            logger.debug(f'  -- wait until: {po}')
            wait.until(EC.visibility_of_element_located(po))
            wk = driver.find_element(*po).text
            wk1 = "/".join(wk.split("\n"))
            logger.debug(f'  wk:[{wk1}]')
            wk2 = re.search(r'.*残り([0-9]+)回分.*', wk)
            wk3 = wk2.group(1)
            logger.debug(f'  wk3:[{wk3}]')
            wk4 = int(wk3)
            logger.debug(f'  -- 残りチップ回数: <{wk4}>')
        except Exception as e:
            logger.info(self.exception_message(e))
            wk4 = 0
        #
        logger.debug(f'  wk4:[{wk4}]')
        return wk4


    def pilot_internal(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug('@@pilot_internal:START')


        logger.info('チップを贈る')
        # ==============================
        ### 汎用性は考えずにチップを処理するだけ。
        cnt = 0
        while True:
            logger.debug('- 「チップを贈る」ダイアログを開き、残数を確認')
            # ------------------------------
            cnt += 1
            remain = self.pilot_internal2()
            if remain > 1:
                logger.debug('- 開かれているダイアログで「贈る」を選択。')
                # ------------------------------
                po = (By.CSS_SELECTOR,"input.btn-primary")
                driver.find_element(*po).click()
                wk5 = False
                for i in range(5):      # 処理待ちチェック：5回までリトライ
                    logger.debug(f'  --i: [{i}]')
                    time.sleep(1.5)
                    wk5 = self.is_alert_present()
                    if wk5 == True: break
                if wk5:
                    wk4 = self.close_alert_and_get_its_text()
                    if not re.search('無料チップを贈りました。$',wk4):
                        break  # exit while    #TODO: Raise ERROR
                else:
                    logger.debug('- チップを遅れませんでした（確認alertなし)')
                    # ------------------------------
                    break   # exit while
            else:
                logger.debug('- チップ残数が 1以下 のため終了')
                # ------------------------------
                break   # exit while
            if cnt >= user['chip_count']:
                # 1回あたりの実施回数＝贈るチップ数
                break   # exit while
            time.sleep(1)
            # end while
        ### logout処理に突入する <- logout処理は driver.get から再開するため、ダイアログは放置。


if __name__ == "__main__":
    import pprint
    try:
        App = MineoChip()
        App.prepare()
        App.pilot('MineoKing', 'MineoChip')
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exception_message(e)}')
        if App.driver:
            wk = str(App.appdict.wkfile("-HC",".png"))
            App.driver.save_screenshot(wk)
            App.driver.quit()
    finally:
        # App.pilot_result.sort(key=itemgetter(0))
        result = App.pilot_result
        if result != []:
            import pprint
            App.report(
                pprint.pformat(result, width=40)
            )
