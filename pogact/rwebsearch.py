# -*- coding: utf-8 -*-
import datetime
import random
from operator import itemgetter
from logging import DEBUG, INFO, WARNING
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logutils.AppDict
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
            self.CLASS_NAME, self.USER_GROUP, __file__,
            '0.2', '$Rev$', 'Alpha'
        )


    def prepare(self, name=None, clevel=None, flevel=None):
        # Excute super() before you use self.logger
        super().prepare(self.appdict.name)

        logger = self.logger
        appdict = self.appdict
        #
        # local settings
        now = datetime.datetime.now()
        appdict.data['today'] = now.replace(hour=0,minute=0,second=0,microsecond=0) 
        appdict.data['need_report'] = 0
        #
        # Start !
        logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")
        logger.debug(f"{appdict.data['today'].strftime('%c')}")


    def pilot_setup(self):
        options = Options()
        options.add_extension("4.663_0.crx")                                # 楽天ウェブ検索をインポート
        # 楽天Web検索はブラウザ拡張を利用するためheadlessモード不可
        # if not __debug__:
        #     options.add_argument(r'--headless')
        options.add_argument("--blink-settings=imagesEnabled=false")        # 画像非表示
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches" , ["enable-automation"])  # disable-infobars

        wk = super().pilot_setup(options)

        if wk is not None:
            self.driver.switch_to.window(self.driver.window_handles[0])

        return wk


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
            what = '//*[@id="contentsBody"]/div[1]/article[2]/h1'
            logger.debug(f'     wait.until: visibility (By.XPATH, "{what}")')
            wait.until(EC.visibility_of_element_located((By.XPATH, what)))
            wk = driver.find_element(By.XPATH, what).text
            logger.debug(f'     [{wk}] == トレンド')

            logger.debug(f'   - ワードを抽出.')
            # ------------------------------
            what = '//*[@id="contentsBody"]/div[1]/article[2]/section/ol/li/a/article'
            word_list = driver.find_elements(By.XPATH,what)
            words = [a.text for a in word_list]
            logger.debug(f'     =>{words}')

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
        cnt = "0"

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
                # レイアウト変更対応
                objects = driver.find_elements(By.XPATH,'//*[@id="wrapper"]/header/div/div[1]/div[1]/div[2]/div/div[1]/span[2]/em')
                if len(objects) > 0:
                    logger.debug(f"    - Found: (By.XPATH, '//*[@id=\"wrapper\"]/header/div/div[1]/div[1]/div[2]/div/div[1]/span[2]/em')")
                else:
                    # 2023/04/15以前
                    logger.debug(f"    - Found: (By.XPATH, '//*[@id=\"wrapper\"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')")
                    objects = driver.find_elements(By.XPATH,'//*[@id="wrapper"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')
                cnt = objects[0].text
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
        logger.debug(f"   {account['name']}: today={appdict.data['today']} vs last={last_done}")
        if appdict.data['today'] > last_done:
            appdict.data['need_report'] += 1

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
        appdict = self.appdict
        logger.debug(f'@pilot(): START')

        self.logger.info(f'- ユーザごとに処理を実行. >{self.USER_GROUP}< >{self.SERVICE_GROUP}<')
        # ==============================
        super().pilot(self.USER_GROUP, self.SERVICE_GROUP)

        self.logger.info(f"- 全処理を完了")
        # ==============================
        # Sort pilot_result[] by NAME of user, and output to logfile.
        self.pilot_result.sort(key=itemgetter(0))
        logger.info(f"Reuslt: {self.pilot_result}")
        # Clear pilot_result[] if no report(mail) is needed.
        logger.debug(f"(need_report = [{appdict.data['need_report']}])")
        if appdict.data['need_report'] == 0:
            self.pilot_result = []

        logger.debug(f'@pilot(): END')


if __name__ == "__main__":
    import pprint
    try:
        rpa = RWebSearch()
        # 設定ファイル読み込み
        rpa.prepare('楽天Webサーチ')
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
