from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, SessionNotCreatedException
from webdrivermanager import ChromeDriverManager
from logging import DEBUG, INFO, WARNING
import pprint
from pathlib import Path
import sys
import random
import time
import datetime
import random
# from logutils import logger, AppDict
import logutils.AppDict
import yaml
from logutils import mailreporter
from RPAbase.RakutenBase import RakutenBase

class RWebSearch(RakutenBase):
    """
    楽天Web検索のポイント山分けに参加する
    """
    CLASS_NAME = 'RWebSearch'
    USER_GROUP = 'Rakuten'
    SERVICE_GROUP = CLASS_NAME

    def __init__(self):
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            self.CLASS_NAME, __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', self.appdict.name)

    def prepare(self):
        super().prepare(self.appdict.name)
        self.today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        self.logger.debug(f"{self.today.strftime('%c')}")
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        options.add_extension("4.648_0.crx")                                # 楽天ウェブ検索をインポート
        # options.add_argument("--headless")        # 楽天Web検索はheadlessモード不可
        options.add_argument("--blink-settings=imagesEnabled=false")        # 画像非表示
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches" , ["enable-automation"])  # disable-infobars

        return super().pilot_setup(options)

    def realtime_words(self):
        """ ヤフーリアルタイム検索よりワード生成 """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug(f' - @realtime_words(): START')

        words = []

        logger.debug(f'  - ヤフーリアルタイム検索より急上昇ワードを取得.')
        # ==============================
        try:
            logger.debug(f'   - サイトを移動.')
            # ------------------------------
            driver.get("http://search.yahoo.co.jp/realtime")
            logger.debug(f'     wait.until: visibility (By.CSS_SELECTOR, "#body > div.Top > article > section")')
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#body > div.Top > article > section")))

            logger.debug(f'   - ワードを抽出.')
            # ------------------------------
            word_list = driver.find_elements_by_css_selector("#body > div.Top > article > section > ol > li > a")
            words = [a.text for a in word_list]
            logger.debug(f'     =>{words}')

            # logger.debug(f'   - 楽天Web検索のadd-onタブで作業していたのでタブを消去する.')
            # # ------------------------------
            # driver.switch_to.window(driver.window_handles[1])
            # driver.close()
            # driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            logger.warn(f'   !!<Ignore>:{self.exception_message(e)}')
            words = []

        logger.debug(f' - @realtime_words(): END')
        return words

    def search_rws(self, words):
        """ 楽天ウェブサーチの実行 """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug(f' - @search_rws(): START')
        cnd = "0"

        logger.debug(f'  - 楽天Web検索を実行.')
        # ==============================
        try:
            logger.debug(f'  - サイトを移動.')
            # ------------------------------
            driver.get("https://websearch.rakuten.co.jp/Web?qt=楽天")
            logger.debug(f'    wait.until: visibility (By.ID, "srchformtxt_qt")')
            wait.until(EC.visibility_of_element_located((By.ID, "srchformtxt_qt"))).clear()

            logger.debug(f'  - 検索開始.')
            # ------------------------------
            random.shuffle(words)
            for word in words:
                logger.debug(f'   - Search Keyword: {word}')
                # ------------------------------
                logger.debug(f'     (Wainting for (By.ID, "srchformtxt_qt")')
                kwarea = wait.until(EC.visibility_of_element_located((By.ID, "srchformtxt_qt")))
                kwarea.clear()
                kwarea.send_keys(word, Keys.ENTER)

                logger.debug(f'     (Wainting for (By.CLASS_NAME, "progress-message")')
                mes = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "progress-message"))).text
                logger.debug(f'   - Search Result: {mes}')

                logger.debug(f'   - Get total search count')
                # 検索画面のレイアウトが２種類できたみたい。 @20200418
                # progress-messageの表示確認が取れていれば、口数情報の取得位置を変えるだけでよさそう。
                # objects = driver.find_elements_by_id("curr-kuchisu-count")
                objects = driver.find_elements_by_xpath('//*[@id="wrapper"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')
                if len(objects) > 0:
                    logger.debug(f"    - Found: (By.XPATH, '//*[@id=\"wrapper\"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')")
                    cnt = objects[0].text
                else:
                    logger.debug(f"    - Found: (By.ID, 'curr-kuchisu-count')")
                    cnt = driver.find_element_by_id("curr-kuchisu-count").text
                logger.debug(f'     Total search count = [{cnt}]')
                if (int(cnt) >= 30):
                    break

            logger.info(f'     検索終了: 本日実績は{cnt}件まで進んでいます')

        except Exception as e:
            logger.warn(f' !!<Ignore>:{self.exception_message(e)}')

        logger.debug(f' - @search_rws(): END')
        return int(cnt)

    def pilot_internal(self, account):
        logger = self.logger
        appdict = self.appdict
        logger.debug(f'- @pilot_internal(): START')

        last_dones = self.last_done.get('RWebSearch',{})

        logger.debug(f' - 実行記録確認.')
        # ==============================
        last_done = last_dones.get(account['name'], datetime.datetime.min)
        logger.debug(f"   {account['name']}: today={self.today} vs last={last_done}")
        if self.today > last_done:

            logger.debug(f' - 急上昇ワードを取得.')
            # ==============================
            words = appdict.data.get('words', None)
            if words is None:
                logger.debug(f'  - 未取得のためYahooを訪問.')
                words = self.realtime_words()
                appdict.data['words'] = words
                logger.debug(f'  - 取得結果: {len(words)}.')
            else:
                logger.debug(f'  - 取得スミのためSKIP.')

            logger.debug(f' - 急上昇ワードを使って検索実行.')
            # ==============================
            random.shuffle(words)
            logger.debug(f'  - 検索開始.')
            cnt = self.search_rws(words)
            if cnt >= 30:
                # 本日分の義務クリア: 実行記録を更新
                last_dones[account['name']] = datetime.datetime.now()
            logger.debug(f'  - 検索終了[{cnt}].')
            self.pilot_result.append( [account['name'],f'ただいまの獲得口数[{cnt}]'] )

            # 実行記録を書き戻し(更新有無は無関係)
            self.last_done['RWebSearch'] = last_dones

        else:
            msg = f"{account['name']}: Already done today.  SKIP."
            logger.info(f'   {msg}')
            self.pilot_result.append(msg)

        logger.debug(f'- @pilot_internal(): END')

    def pilot(self):
        logger = self.logger
        logger.debug(f'@pilot(): START')

        self.logger.info(f'- ユーザごとに処理を実行. >{self.USER_GROUP}< >{self.SERVICE_GROUP}<')
        # ==============================
        super().pilot(self.USER_GROUP, self.SERVICE_GROUP)

        self.logger.info(f"- 全処理を完了")
        # ==============================
        logger.info(f'Result: {self.pilot_result}')
        logger.debug(f'oo {self.last_done}')
        if self.pilot_result != []:
            report = sorted(self.pilot_result, key=lambda x: x[0])
            self.reporter.critical(f" 処理結果: {pprint.pformat(report,width=64)}")

        logger.debug(f'@pilot(): END')


if __name__ == "__main__":
    try:
        App = RWebSearch()
        App.prepare()
        App.pilot()
        App.tearDown()
    except Exception as e:
        App.logger.critical(f'!!{App.exceptionMessage(e)}')
