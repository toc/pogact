import time
import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import RPAbase.TimesCarShare
import logutils.AppDict

class TCSReceipt(RPAbase.TimesCarShare.TimesCarShare):
    """
    Times Car Shareの利用履歴、利用証明をダウンロードする。
    毎月10日ころに前月分を取得する運用を想定している。

    ◎Times Car Share公式のよくある質問より:
    https://share.timescar.jp/faq/mypage/17.html
    Q 毎月の合計利用金額が確定するタイミングはいつですか？
    A 毎月の合計利用金額は、翌月3営業日に確定いたします。
      なお、利用金額が確定するまでは、利用明細がダウンロードいただけません。
      合計利用金額が確定後にダウンロードをお願いいたします。
    """

    def __init__(self):
        self.super = super(TCSReceipt, self)
        self.super.__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            r'TCSReceipt', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        self.super.prepare(self.appdict.name)
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")
        # PDF保存準備
        dldir = Path(__file__).with_name('pdfdownload')
        dldir.mkdir(exist_ok=True)  # 存在していてもOKとする（エラーで止めない）
        self.appdict.data['download_dir'] = str(dldir.resolve())  # absolute path.

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # PDF保存準備
        options.add_experimental_option("prefs", {
            "download.default_directory": self.appdict.data['download_dir'],
            "plugins.always_open_pdf_externally": True
        })
        return super().pilot_setup(options)


    def pilot_internal1(self):
        """
        利用履歴ページを開き対象年月ごとに詳細ページの有無とそのURLを取得する。
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        result = {}
        result_cnt = 0

        try:
            # 利用履歴ページへ移動
            driver.get('https://share.timescar.jp/view/use/list.jsp')
            # 表示待ち: 「ご利用履歴・明細」
            logger.debug('  wait for (By.ID, r"isExistsPastUse")')
            wait.until(EC.element_to_be_clickable((By.ID, r'isExistsPastUse')))
            rows = driver.find_elements(By.XPATH,r'//*[@id="isExistsPastUse"]/table/tbody/tr')
            for row in rows:
                yymm = ""
                link = ""
                logger.debug(f'  -- [{row.text}]')
                cols = row.find_elements(By.XPATH,"td")
                if len(cols) == 0:
                    logger.debug('   !! it must be table header(th) record.  Skip.')
                    continue
                # ---
                result_cnt += 1
                yymm = cols[0].text
                logger.debug(f'  -- Found: {yymm}.')
                links = cols[6].find_elements(By.XPATH,"a")
                if len(links) > 0:
                    link = links[0].get_attribute(r'href')
                result[yymm] = link
                logger.debug(f'  -- {yymm}: {link}')
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Parsing mail list: {type(e)} {e.args}')

        return result_cnt, result
    
    def pilot_internal2(self, history, yy, mm):
        """
        月別利用履歴リストのうち、yy,mmで指定された年月の詳細情報をダウンロード、保存する。
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        sts = 0
        try:
            yymm = format(yy, '04d') + '年' + format(mm, '02d') + '月'
            link = history[yymm]
            logger.debug(f'  -- Try to get certificates at {yymm}.')
            if len(link) > 0:
                # 詳細ページあり -> そのページへ移動
                driver.get(link)
                # 月間利用証明を取得
                logger.info(f'  --- Try to get monthly certificate at {yymm}')
                tmpobj = driver.find_element(By.ID,r'goResultDetailPdf')
                tmplink = tmpobj.get_attribute(r'href')
                logger.debug(f'  ---- Try to get {tmplink}')
                driver.get(tmplink)
                time.sleep(1)  # PDF保存のため一定時間URL移動を避ける
                # 個別利用証明を取得
                logger.info(f'  --- Try to get each certificates at {yymm}')
                ##　実績テーブル中の利用証明書リンクを取得
                tab = driver.find_element(By.XPATH,r'//*[@id="d_past"]/table[1]')
                evidences = tab.find_elements(By.LINK_TEXT,'ご利用証明書ダウンロード')
                ## 利用証明書リンクからPDFダウンロード
                for evidence in evidences:
                    tmplink = evidence.get_attribute("href")
                    logger.debug(f'  ---- Try to get {tmplink}')
                    driver.get(tmplink)
                    time.sleep(1)  # PDF保存のため一定時間URL移動を避ける
        except Exception as e:
            sts = -99
            logger.error(f' Caught Ex(Ignore): Parsing mail list: {type(e)} {e.args}')

        return sts

    def pilot(self):
        self.pilot_setup()

        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        try:
            all_users = self.config.get(r'TimesCarShare', [])
            logger.debug(f'  -- {all_users}')
            target_users = self.config.get(appdict.name, [])
            for user in all_users:
                logger.debug(f'  -- try {user}')
                if user['name'] not in target_users:
                    # 実行対象外ユーザはスキップ
                    continue
                # ユーザ情報のロギング
                wk = user.copy()
                wk.pop('pw')
                logger.debug(f" Processing for user: {wk}")
                if self.pilot_login(user):
                    num, detail_dict = self.pilot_internal1()

                    # now = datetime.datetime.now()
                    # diff = relativedelta(months=2) if now.day <= 10 else relativedelta(months=1)
                    # target_day = now - diff 
                    # logger.debug(f'  - taget: {target_day.year}/{target_day.month}')
                    # sts = self.pilot_internal2(detail_dict, target_day.year, target_day.month)
                    for mm in range(1,12):
                        sts = self.pilot_internal2(detail_dict, 2022, mm)

                    self.pilot_logout()
                else:
                    logger.error(f'Login failed for user(SKIP): <{user["id"]}>')
        except Exception as e:
            logger.error(f"Caught exception: {type(e)} {e.args}")


if __name__ == "__main__":
    App = TCSReceipt()
    App.prepare()
    App.pilot()
    App.tearDown()
