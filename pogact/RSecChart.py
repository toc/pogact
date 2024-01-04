# -*- coding: utf-8 -*-
import datetime
import time
import yaml
from dateutil.relativedelta import relativedelta
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
import RPAbase.RSecBase
import logutils.AppDict

class RSecChart(RPAbase.RSecBase.RSecBase):

    def __init__(self, param_type):
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'RSecChart', 'RakutenSec', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.appdict.data['param_type'] = param_type

    def prepare(self):
        """
        """
        status = super().prepare(self.appdict.name)
        #
        logger = self.logger
        appdict = self.appdict
        #
        logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")
        # ----------------------------------
        self.last_done[self.appdict.name] = self.last_done.get(self.appdict.name,{})
        # 
        logger.debug(f"  -- 実施ずみチェック")
        # ----------------------------------
        previous = self.last_done[self.appdict.name].get('execute_at', datetime.datetime.min)
        logger.debug(f'    previous[{previous}] vs now[{self.appdict.data["now"]}]')
        wk = appdict.data['now']
        if  previous > wk - relativedelta(hours=1):
            # 本日すでに実施済みならSKIP
            logger.info(f"   実施ずみのためSKIP[{previous}]")
            self.pilot_result.append(f"   実施ずみのためSKIP[{previous}]")
            return False
        #
        logger.debug(f"  -- パラメータファイル読み込み")
        # ----------------------------------
        try:
            param_file = f'params/RSecChart_{appdict.data["param_type"]}.yaml'
            with open(param_file, 'r', encoding='utf-8') as f:
                self.params = yaml.safe_load(f)
                pprint.pprint(self.params)
        except Exception as e:
            logger.error(self.exception_message(e))
            raise e
        #
        logger.debug(f"  -- イメージ保存場所準備")
        # ----------------------------------
        today_str = f'{str(wk.year).zfill(4)}{str(wk.month).zfill(2)}{str(wk.day).zfill(2)}_{appdict.data["param_type"]}T{str(wk.hour).zfill(2)}'
        dldir = Path('C:\\temp\\today').with_name(today_str)
        dldir.mkdir(exist_ok=True)  # 存在していてもOKとする（エラーで止めない）
        appdict.data['download_dir'] = str(dldir.resolve())  # absolute path.
        # index.md作成
        mdfile = dldir / 'index.md'
        with open(dldir.with_name(f'{appdict.data["param_type"]}.md'), 'r', encoding='utf-8') as f:
            comment = f.read()
        with open(mdfile, 'w', encoding=r'utf-8') as f:
            comment_tmpl = '''
## コメントテンプレ
- 市況全般

|項目         |自分の見解|備考                             |
|:------------|:---------|:--------------------------------|
|市況の流れ   |          |---------------------------------|
|経済/指数動向|          |---------------------------------|
|売買理由     |          |買う/売る/様子見                 |

- 銘柄単位

|項目         |自分の見解|備考                             |
|:------------|:---------|:--------------------------------|
|銘柄動向   |          |経済指数やチャートから |
|売買理由     |          |買う/売る/様子見                 |
|反省点       |          |次に活かせるように               |
|損切り       |          |タイミングは適切？早すぎ/遅すぎ？|
'''
            f.write(f'# {today_str}\n\n銘柄一覧\n\n## コメント\n{comment}\n\n{comment_tmpl}')
        #
        logger.info(f'- @prepare(): DONE / [{status}]')
        # ----------------------------------
        return status

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        # prof_path = Path(__file__).with_name('profiles') / self.appdict.name
        # options.add_argument(f'--user-data-dir={str(prof_path)}')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # PDF保存準備
        options.add_experimental_option("prefs", {
            # "download.default_directory": self.appdict.data['download_dir'],
            "plugins.always_open_pdf_externally": True
        })
        return super().pilot_setup(options, disable_password_manager=True)


    def pilot_internal1(self, target):
        """
        チャートの初期設定
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        markets = {'国内株式': 0, '米国株式':1, '投資信託':3}
        result_cnt = 0
        #
        #
        try:
            logger.info(f" -- 銘柄検索 / for {target}")
            # ----------------------------------
            #
            logger.debug(f" -- 銘柄に移動し詳細チャートを表示 / for {target}")
            # ----------------------------------
            if type(target) is list:
                (market, stock) = target
            else:
                market = '国内株式'
                stock = target
            po = (By.NAME, 'stoc-type-01')
            logger.debug(f'  wait for {po}; 検索ボックス待ち')
            wait.until( EC.visibility_of_element_located(po))
            # 市場選択
            driver.find_element(*po).click()
            Select(driver.find_element(*po)).select_by_visible_text(market)
            # 銘柄指定
            po = (By.ID, 'search-stock-01')
            driver.find_element(*po).clear()
            driver.find_element(*po).send_keys(stock + Keys.ENTER)
            # チャートへ移動
            po = (By.LINK_TEXT, 'チャート')
            logger.debug(f'  wait for {po}; チャートへ移動')
            wait.until( EC.visibility_of_element_located(po))
            elem = driver.find_element(*po)
            logger.debug(f'  -- elem[{elem}]')
            driver.execute_script('arguments[0].click();', elem)
            #
            po = (By.TAG_NAME, 'input')
            inputs = driver.find_elements(*po)
            for elem in inputs:
                if elem.get_attribute('alt') == 'テクニカルチャート':
                    break
            logger.debug(f'  -- elem[{elem}]')
            driver.execute_script('arguments[0].click();', elem)
            #
            while True:
                logger.debug(f'  ... waiting TECHNICAL-CHART-WINDOW')
                if len(driver.window_handles) > 1:
                    break
                time.sleep(0.5)
            #
            driver.switch_to.window(driver.window_handles[1])
            driver.maximize_window()
            #
            logger.debug(f" -- テクニカル分析追加 / for {target}")
            # ----------------------------------
            targ = ["101", "13", "404"]    # 101 ポリんじゃーバンド(BB), 404 RSI, 13 MACD
            # 単純移動平均と出来高はプリセットされている前提
            for id in targ:
                po_ta = (By.ID, 'mi-ta')    # テクニカル分析マーク
                driver.find_element(*po_ta).click()
                po = (By.XPATH, '//*[@id="msi-ta"]')
                elems = driver.find_elements(*po)
                # logger.debug(f'  -- [{len(elems)}]')
                for elem in elems:
                    seq = elem.get_attribute('seq')
                    if seq == id:
                        logger.debug(f'  -- found[{id}][elem.get_attribute("name")]')
                        elem.click()
                        # time.sleep(1)
                        break
                # menuを閉じる
                driver.find_element(*po_ta).click()
            #
            logger.debug(f" -- チャート画像採取 / for {target}")
            # ----------------------------------
            po = (By.XPATH, '//body')    # HTMLの中央
            symbol = driver.find_element(*po)
            actions = ActionChains(driver)
            actions.click(symbol)
            actions.move_by_offset(890,-30)     # 最新日に移動 … 画面サイズにより調整要
            actions.perform()
            hc_path = Path(self.appdict.data['download_dir']) / (stock + '.png')
            driver.save_screenshot(str(hc_path))
            #
            po = (By.CSS_SELECTOR, '#c5widget > div.toolbar > div.mainricinputbox > div > div.displaybox.modebox > div > span.nm')    # 銘柄名
            stock_name = driver.find_element(*po).text
            logger.debug(f" ---- stock_name[{stock_name}]")
            #
            logger.info(f" -- チャート採取終了 / for {target}")
            # ----------------------------------
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            pass
        except Exception as e:
            logger.warn( self.exception_message(e, '想定外の例外発生') )

        return stock_name
    
    def pilot_internal(self, account):
        """
        銘柄リスト取得
        """
        logger = self.logger
        appdict = self.appdict
        params = self.params
        #
        name = params.get('name', 'DEFAULT')
        usable_markets = ["国内株式","米国株式","投資信託"]
        dldir = Path(appdict.data['download_dir'])
        mdfile = dldir / 'index.md'
        #
        logger.info(f' - Collet stock chart for {name}: START')
        try:
            stock_groups = params.get('stocks',{})
            if len(stock_groups) > 0:
                for market in stock_groups.keys():
                    #
                    logger.debug(f" -Check MARKET")
                    # ----------------------------------
                    if len(market) <= 0 or market not in usable_markets:
                        logger.debug(f'  -- The market {market} is not able to treat.  SKIP.')
                        continue
                    stocks = stock_groups[market]
                    if stocks is None or len(stocks) == 0:
                        # No item.
                        logger.debug(f'  -- There is no target.  SKIP. [market<{market}>,stock<{stocks}>]')
                        continue
                    #
                    logger.debug(f' - market[{market}]: START..')
                    # Add md text: market
                    with open(mdfile, 'a', encoding=r'utf-8') as f:
                        f.write(f'## {market}\n\n')
                    for stock in stocks:
                        logger.debug(f'  - Try [{market}][{stock}].')
                        # Get chart image
                        stock_name = self.pilot_internal1([market,stock])
                        # Add md text: stock
                        with open(mdfile, 'a', encoding=r'utf-8') as f:
                            f.write(
                                f'### {stock}: {stock_name}\n\n' \
                                + f'[<img src="{stock}.png" alt="日足チャート" title="{stock_name}" width=480>]({stock}.png)\n\n'
                            )
                    # end // stock
                    logger.debug(f' - market[{market}]: DONE')
                # end // stock_group

                self.last_done[self.appdict.name]['execute_at'] = self.appdict.data['now']
            else:
                logger.warn(f'!! No stock group is defined.  CHECK parameter file first.')
        except Exception as e:
            self.logger.error(self.exception_message(e))
        finally:
            logger.info(f' - Collet stock chart: DONE.')
            pass


if __name__ == "__main__":
    from argparse import ArgumentParser, RawTextHelpFormatter
    usage = 'python {} TYPE [--help]'.format(__file__)
    argparser = ArgumentParser(
        usage=usage,
        # description='type',
        formatter_class=RawTextHelpFormatter
    )
    argparser.add_argument(
        'param_type', type=str,
        help="Suffix of parameter file(YAML format), which MUST exist <script folder>/params/RSecChart_<param_type>.yaml.\n"
        + "  No argument is supposed to be specify 'daily'."
    )
    args = argparser.parse_args()
    try:
        from logging import WARNING, DEBUG
        import pprint
        App = RSecChart(args.param_type)
        if App.prepare() is not False: # '楽天証券_チャート取得') # ,clevel=WARNING)
            App.pilot('RakutenSec','RSecChart')
        else:
            App.logger.warn('既に実施ずみのためSKIP')
        pprint.pprint(App.pilot_result, width=80, compact=True)
        App.tearDown()
    except Exception as e:
        print(App.exception_message(e))
        if App:
            if App.driver:
                App.driver.quit()
