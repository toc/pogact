# -*- coding: utf-8 -*-
import time
import datetime
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from logging import DEBUG, INFO    # , WARNING, ERROR, CRITICAL
from bs4 import BeautifulSoup
import logutils.AppDict
from RPAbase.AOLbase import AOLbase
import RPAbase.ECnaviBase


class AOLmail(AOLbase):
    """
    """
    def __init__(self):
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'AOLmail', 'AOLmail', __file__,
            '0.2', '$Rev$', 'Alpha'
        )


    def prepare(self, name=None, clevel=None, flevel=None):
        super().prepare(self.appdict.name)
        self.today = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        self.logger.debug(f"{self.today.strftime('%c')}")
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")


    def pilot_setup(self,username=None):
        options = Options()
        if not __debug__:
            options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return super().pilot_setup(options,username, waitsec=20)

    def pilot_internal_visit(self, name, sitename, site):
        """
        対象サイトごとにログインした状態で収集したURL(link)を訪問する。
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(f' @@pilot_internal_visit:START[{sitename}]')

        logger.info(f' 初期チェック:{sitename}')
        # ==============================
        logger.debug(' - 訪問リンク数を確認')
        # ------------------------------
        num_ptlinks = len(appdict.data['ptlinks'][name].get(sitename,[]))
        logger.debug(f'   - 対象リンク数[{num_ptlinks}]')
        if num_ptlinks == 0:
            # 処理すべきリンクなし。
            return [0,0]

        logger.debug(f' - {sitename}のユーザ情報を取得')
        # ------------------------------
        users_in_site = self.config.get('users',{}).get(sitename,{})
        logger.debug(f'   - users in site:>{[user["name"] for user in users_in_site]}<')
        for user in users_in_site:
            if user['name'] == name:
                logger.debug(f'     - found: >{name}<')
                break
        wk = user.copy()
        for i in ['pw','pin','charge_pw','hint']:
            if wk.get(i): wk.pop(i)
        logger.debug(f'   - selected: >{wk}<')

        logger.info(f' {sitename}にログイン')
        # ==============================
        if len(driver.window_handles) < 2:
            logger.debug('   - 新規タブを作成')
            # ------------------------------
            driver.execute_script("window.open()")
        driver.switch_to.window(driver.window_handles[1])

        logger.debug(f'   - {sitename}: ログインページにアクセス')
        # ------------------------------
        site.pilot_login(user)

        logger.info(' ポイントURLに順次アクセス')
        # ==============================
        not_visited = []
        total_count = 0
        for link in appdict.data['ptlinks'][name][sitename]:
            total_count += 1
            try:
                logger.debug(f' - ポイントURLアクセス({total_count}/{num_ptlinks})')
                # ------------------------------
                driver.get(link)
                logger.debug(f'  --wait.until visibility_of_element_located((By.TAG_NAME,"body"))')
                wait.until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
                time.sleep(1)
                logger.info(f'  - SUCCESS: {link}')
            except Exception as e:
                logger.warn(f'  - FAIL(SKIP): {link}')
                # ------------------------------
                logger.debug(f'  -- exception: {self.exception_message(e)}')
                not_visited.append(link)
        logger.debug(f'  -- アクセス結果: Total={total_count}, NG={len(not_visited)}')
        appdict.data['ptlinks'][name][sitename] = not_visited

        logger.info(f' {sitename}からログアウト')
        site.pilot_logout(user)
        driver.switch_to.window(driver.window_handles[0])

        logger.debug(f' @@pilot_internal_visit:END[{sitename}]')
        return [total_count - len(not_visited), len(not_visited)]

    def pilot_internal(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger

        try:
            # setup MIX-in modules.
            #TODO: 名前からインスタンス化できればスッキリ書けそう！
            self.appdict.data['sites'] = []
            ### Moppy
            wk = RPAbase.ECnaviBase.ECnaviBase()
            wk.silent_setup(driver, wait, self.logger)
            self.appdict.data['sites'].append(['ECnavi',wk])


            logger.info('-- driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")')
            driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")

            logger.debug('受信箱に移動')
            # ------------------------------
            pageobj = (By.NAME, "msgListForm")
            # logger.debug(f'-- WAIT:visibility_of_element_located({pageobj})')
            # wait.until(EC.visibility_of_element_located(pageobj))
            logger.debug(f'-- WAIT:element_to_be_clickable({pageobj})')
            wait.until(EC.element_to_be_clickable(pageobj))
            # driver.find_element(*pageobj).click()

            self.appdict.data['ptlinks'] = {}
            self.appdict.data['ptlinks'][user['name']] = {}
            self.appdict.data['ptlinks'][user['name']]['ECnavi'] = []
            self.appdict.data['log'] = {}
            self.appdict.data['log'][user['name']] = []

            mail_unread, mail_havelink = (0,0)
            while True:
                logger.debug('受信箱に移動')
                # ------------------------------
                # wait until message list is displayed.
                pageobj = (By.ID,"messageListContainer")
                logger.debug(f'-- WAIT:visibility_of_element_located({pageobj})')
                wait.until(EC.visibility_of_element_located(pageobj))
                # fetch message list.
                # pageobj=(By.CSS_SELECTOR,".dojoxGrid-content")
                content = driver.find_element(*pageobj)
                rows = content.find_elements(By.XPATH,"tbody/tr")
                row_count = len(rows)
                # row_count = 20
                logger.debug(f'  -- rows:{row_count}')

                for row in rows:
                    row_count -= 1
                    logger.debug('  メールごとの処理')
                    # ------------------------------
                    if row.get_attribute('data-test-id') is None:
                        # tr にこの属性↑をもっていなければＳＫＩＰ
                        continue
                    # ------------------------------
                    logger.debug(f'- Open message')
                    pageobj = (By.XPATH,'td')
                    tds = row.find_elements(*pageobj)
                    for td in tds:
                        logger.debug(f'  ==[{td.text}]')
                    subject = row.text
                    logger.debug(f'  -- subject[{subject}]')
                    # ### already READ?
                    # wk = row.get_attribute('class').split()
                    # if 'row-read' in wk:
                    #     logger.debug(f'  -- This mail is already read.  SKIP.')
                    #     continue
                    ### unread mail is found.  go into the message.
                    mail_unread += 1
                    row.click()
                    # pageobj = (By.CSS_SELECTOR,".subject")
                    pageobj = (By.XPATH,'//*[@id="content"]/table/tbody')
                    logger.debug(f'-- WAIT:visibility_of_element_located({pageobj})')
                    wait.until(EC.visibility_of_element_located(pageobj))
                    wk = driver.find_element(*pageobj)
                    # wk2 = wk.text
                    # logger.debug(f'  -- subject[{wk2}]')
                    # if wk2 != subject[:len(wk2)]:
                    #     raise Exception('Subjectが違います')
                    ### Fetch URLs in the message.
                    links = []
                    soup = BeautifulSoup(driver.page_source,"lxml")
                    lists = soup.select("a")
                    # URL末尾に / および 半角SPC がつくときがある。
                    regex = re.compile(r'^https://ecnavi.jp/m/go/\S+/?\s*$', re.A)
                    for l in lists:
                        wk = l.get("href")
                        # logger.debug(f'  >>{wk}<<')
                        if regex.match(wk):
                            links.append(wk)
                            logger.debug(f'--FOUND:a href={wk}')
                    self.appdict.data['ptlinks'][user['name']]['ECnavi'].extend(links)
                    ### mail analisys is completed.  back to mail list.
                    # pageobj = (By.TAG_NAME,"body")
                    # logger.debug(f'-- WAIT:visibility_of_element_located({pageobj})')
                    # wait.until(EC.visibility_of_element_located(pageobj))
                    # if len(links) > 0:
                    #     # have link: delete mail
                    #     logger.debug(f'-- Found link(s) [{len(links)}].')
                    #     wk_key = Keys.DELETE
                    #     mail_havelink += 1
                    # else:
                    #     # have no link: skip mail
                    #     logger.debug(f'-- No links.  SKIP!')
                    #     wk_key = "x"
                    # driver.find_element(*pageobj).send_keys(wk_key)
                    pageobj = (By.XPATH,'//*[@id="msgListForm"]/div/span[1]/button[1]')
                    driver.find_element(*pageobj).click()
                    break               # End loop: for

                if row_count <= 0:
                    # 最終メールまで処理済み→終了
                    wk = ['ECnavi']
                    wk2 = f'New[{mail_unread}]->[{mail_havelink}, SKIP:{mail_unread - mail_havelink}]'
                    logger.debug(f'  - {wk2}')
                    wk.append([wk2])
                    wk.append( self.appdict.data['ptlinks'][user['name']]['ECnavi'] )
                    self.appdict.data['log'][user['name']].append(wk)
                    break               # End loop: while
                else:
                    # ファイルを削除した場合は一覧表示の更新を待つ必要あり
                    time.sleep(1.5)
        except Exception as e:
            logger.error(f'Caught exception while analyzing mails: {self.exception_message(e)}')
            logger.error(f'Raise exception and exit!')
            raise(e)

        try:
            logger.info('抽出したポイント付きURLを訪問')
            # ==============================
            # メール一覧に対象がなくても一時保存URLが残っていれば処理が必要。
            cnt_OK, cnt_NG, sum_OK, sum_NG = [0, 0, 0, 0]
            for i in self.appdict.data['sites']:
                cnt_OK, cnt_NG = self.pilot_internal_visit(user['name'], i[0], i[1])
                sum_OK += cnt_OK
                sum_NG += cnt_NG
            self.appdict.data['log'][user['name']].append(f'Visited: o={sum_OK} / x={sum_NG}')

            # logger.info(f'アクセスできなかったURLを一時保存(次回処理)')
            # # ==============================
            # logger.debug(f'- 一時保留URL={sum_NG}')
            # fname = str(self.appdict.name).lower()
            # with open(f'{fname}_remain.yaml', 'w', encoding='utf-8') as f:
            #     #TODO: last_done.yamlで手当できないか？
            #     yaml.dump(self.appdict.data['ptlinks'], f, default_flow_style=False, allow_unicode=True)
            # self.appdict.data['log'][user['name']].append(f'Save not-visited URLs. {sum_NG} link(s).')
        except Exception as e:
            logger.error(f'Caught exception while visiting URLs: {self.exception_message(e)}')
            logger.error(f'Raise exception and exit!')
            raise(e)


        if (sum_OK,sum_NG) != (0,0):
            # Report result.
            self.pilot_result.append([user['name'],self.appdict.data['log'][user['name']]])
        logger.debug('@@pilot_internal: END')


if __name__ == "__main__":
    import pprint
    try:
        rpa = AOLmail()
        # 設定ファイル読み込み
        rpa.prepare('AOL mail')
        # ブラウザ操作
        # -- Webdriverの準備からquitまで実施する
        rpa.pilot()
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
        # ブラウザの後始末
        rpa.tearDown()
