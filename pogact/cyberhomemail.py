# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import time, re
from bs4 import BeautifulSoup
import yaml
import logutils.AppDict
import RPAbase.CyberhomeBase
from RPAbase.InfoseekBase import RakutenBase
import RPAbase.MoppyBase
import RPAbase.HapitasBase
import RPAbase.SBIgroupBase
import RPAbase.PointIncomeBase
import RPAbase.PointStadiumBase

class CyberhomeMail(RPAbase.CyberhomeBase.CyberhomeBase):
    """
    """
    def __init__(self):
        """
        Constructor for this class.
        1. Create instance variable.
        """
        super().__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            'CyberhomeMail', 'CyberhomeMail', __file__,
            '0.2', '$Rev$', 'Alpha'
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
        # setup MIX-in modules.
        #TODO: 名前からインスタンス化できればスッキリ書けそう！
        self.appdict.data['sites'] = []
        ### Moppy
        wk = RPAbase.MoppyBase.MoppyBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['Moppy',wk])
        ### Hapitas
        wk = RPAbase.HapitasBase.HapitasBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['Hapitas',wk])
        ### SBIgroup
        wk = RPAbase.SBIgroupBase.SBIgroupBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['SBIgroup',wk])
        ### PointIncome
        wk = RPAbase.PointIncomeBase.PointIncomeBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['PointIncome',wk])
        ### PointStadium
        wk = RPAbase.PointStadiumBase.PointStadiumBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['PointStadium',wk])
        ### Rakuten
        # wk = RPAbase.RakutenBase.RakutenBase()
        wk = RakutenBase()
        wk.silent_setup(driver, wait, self.logger)
        self.appdict.data['sites'].append(['Rakuten',wk])

        return [driver,wait]


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
        if len(users_in_site) == 0:
            # 対象サイトの利用なし
            logger.warn(f'    - no users exist in sitename[{sitename}].  SKIP.')
            return [0,0]
        
        logger.debug(f'   - users in site:>{[user["name"] for user in users_in_site]}<')
        for user in users_in_site:
            if user['name'] == name:
                logger.debug(f'     - found: >{name}<')
                break
        wk = user.copy()
        for i in ['pw','pin','charge_pw','hint']:
            if wk.get(i): wk.pop(i)
        logger.debug(f'   - selected: >{wk}<')

        logger.info(f' ポイントURL訪問')
        # ==============================
        if len(driver.window_handles) < 2:
            logger.debug('   - 新規タブを作成')
            # ------------------------------
            driver.execute_script("window.open()")
        driver.switch_to.window(driver.window_handles[1])
        total_count = 0
        not_visited = []
        try:
            logger.debug(f'   - {sitename}: ログインページにアクセス')
            # ------------------------------
            site.pilot_login(user)

            logger.info(' ポイントURLに順次アクセス')
            # ------------------------------
            for link in appdict.data['ptlinks'][name][sitename]:
                total_count += 1
                try:
                    logger.debug(f' - ポイントURLアクセス({total_count}/{num_ptlinks})')
                    # ------------------------------
                    driver.get(link)
                    logger.debug(f'  --wait.until visibility_of_element_located((By.TAG_NAME,"body"))')
                    wait.until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
                    if sitename == 'PointStadium':
                        clicked = False
                        for i in range(10):
                            try:
                                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.vbtn')))
                                driver.find_element(By.CSS_SELECTOR,'.vbtn').click()
                                clicked = True
                                time.sleep(1)
                                break
                            except ElementClickInterceptedException as e:
                                driver.find_element(By.TAG_NAME,"body").send_keys(Keys.PAGE_DOWN)
                                pass
                        # 作業用Windowを閉じて、最新のWindowに移動
                        if clicked:
                            driver.switch_to.window(driver.window_handles[-1])
                            driver.close()
                            driver.switch_to.window(driver.window_handles[-1])
                            time.sleep(1)
                            logger.info(f'  - SUCCESS: {link}')
                        else:
                            logger.error(f'  -- Cannot click .vbtn @ PointStadium.')
                except Exception as e:
                    logger.warn(f'  - FAIL(SKIP): {link}')
                    # ------------------------------
                    logger.debug(f'  -- exception: {self.exception_message(e)}')
                    not_visited.append(link)
            logger.debug(f'  -- アクセス結果: Total={total_count}, NG={len(not_visited)}')
            appdict.data['ptlinks'][name][sitename] = not_visited

            logger.info(f' {sitename}からログアウト')
            site.pilot_logout(user)
        except Exception as e:
            logger.warn(f'  -- exception: {self.exception_message(e)}')
            logger.warn(f'    -- all links remains as NOT VISITED. [{len(appdict.data["ptlinks"][name][sitename])}]')
            pass
        finally:
            driver.switch_to.window(driver.window_handles[0])

        logger.debug(f' @@pilot_internal_visit:END[{sitename}]')
        return [total_count - len(not_visited), len(not_visited)]


    def pilot_internal_pickup_url_moppy(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - moppyを想定してメール本文を解析')
        # ------------------------------
        links = []

        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^https://pc.moppy.jp/(clc/\?clc_tag|cc/c\?t)=\S+$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                links.append(wk)
                logger.debug(f'--FOUND:a href={wk}')

        # URLリストを返却、空リストなら対象なし(Moppyメール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def pilot_internal_pickup_url_pointstadium(self, subj, fr):
        """
        PointStagium用広告操作
        - PointStagiumは広告リンク(STEP2)をjavascriptで制御。
        - 広告リンクを保存できないためこのタイミングで広告もクリックする。
        """
        driver = self.driver
        logger = self.logger

        logger.debug('  - PointStadiumを想定してメール本文を解析')
        # ------------------------------
        links = []
        # num_wins = len(driver.window_handles) 
        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^https://www.point-stadium.com/mclick.asp\?pid=toc.tanaka&\S+$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                # 広告メール(STEP1)発見
                logger.debug(f'   --- 広告STEP1候補>{wk}<')
                links.append(wk)
                logger.debug(f'   --- 広告STEP1は1件目のみを対象とする(メールポイントは１つ目オンリーのハズ？？)')
                break
        # URLリストを返却、空リストなら対象なし
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def pilot_internal_pickup_url_hapitas(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - hapitasを想定してメール本文を解析')
        # ------------------------------
        links = []

        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^https://r34.smp.ne.jp/u/\S+\.html$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                links.append(wk)
                logger.debug(f'--FOUND:a href={wk}')

        # URLリストを返却、空リストなら対象なし(Hapitasメール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def pilot_internal_pickup_url_sbigroup(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - sbiポイントを想定してメール本文を解析')
        # ------------------------------
        links = []

        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^http://www7.webcas.net/mail/u/l\?p=\S+$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                links.append(wk)
                logger.debug(f'--FOUND:a href={wk}')

        # URLリストを返却、空リストなら対象なし(SBIポイントメール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links

    def pilot_internal_pickup_url_pointincome(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - PointIncomeを想定してメール本文を解析')
        # ------------------------------
        links = []

        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^https://pointi.jp/al/click_mail_magazine.php?\S+$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                links.append(wk)
                logger.debug(f'--FOUND:a href={wk}')

        # URLリストを返却、空リストなら対象なし(Moppyメール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links

    def pilot_internal_pickup_url_rakuten(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - 楽天Mail de pointを想定してメール本文を解析')
        # -----------------------------------------------------------
        logger.debug('    - イメージリンクボタンをチェック')
        # ================================================
        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a img")        # a内に子タグとしてimgが存在するものを抽出
        links = []
        for l in lists:
            wk = l.get("src")
            if wk in (
                "https://point-g.rakuten.co.jp/mailmag/common/pg_click_banner_btn.png",
                "http://point-g.rakuten.co.jp/mailmag/common/pg_click_banner_btn.png",
                "https://point-g.rakuten.co.jp/mailmag/common/pg_click_banner_btn_2.png",
                "https://image.books.rakuten.co.jp/books/img/bnr/other/group/201811/point-click-201811-main.png",
                "https://edy.rakuten.co.jp/htmlmail/ad/images/btn_get.gif",
                "https://image.infoseek.rakuten.co.jp/content/tmail/htmlmail/bnr_03b.png",
                ):
                links.append(l.parent.get("href"))
                logger.debug(f'      --FOUND:img src={wk}')
                logger.debug(f'      --STORED href={l.parent.get("href")}')
        logger.debug(f'    -> num links is [{len(links)}]')

        logger.debug('    - テキストリンクをチェック')
        # ==========================================
        link_regex = r'https://pg.rakuten.co.jp/act\?.*'
        regex = re.compile(link_regex)
        logger.debug(f'   -- Compare with >{link_regex}<')
        lists = soup.find_all("a", string=regex)        # filter by link text
        for l in lists:
            wk = l.string
            if wk is not None:
                links.append(wk)
                logger.debug(f'   --STORED href={wk}')

        # URLリストを返却、空リストなら対象なし(楽天メール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def open_url_tree(self, user):
        logger = self.logger
        logger.debug('Cyberhome: open_url_tree: 開始')
        ptlinks = self.appdict.data['ptlinks'][user['name']]
        # print([x for x in ptlinks])
        num_ptlinks = [len(ptlinks[x]) for x in ptlinks]
        # print(num_ptlinks)
        logger.debug('Cyberhome: open_url_tree: 終了')
        return num_ptlinks


    def pilot_internal(self, user):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        logger.debug('@@pilot_internal:START')

        logger.info('Cyberhome未読メール: 解析開始')
        # ==============================
        if self.appdict.data.get('log') is None:
            self.appdict.data['log'] = {}
        self.appdict.data['log'][user['name']] = []
        #
        logger.debug(f"  -- self.appdict.data['ptlinks']={self.appdict.data['ptlinks']}")
        if self.appdict.data['ptlinks'] is None:
            self.appdict.data['ptlinks'] = {}
        ptlinks = self.appdict.data['ptlinks'].get(user['name'],{})
        self.appdict.data['ptlinks'][user['name']] = ptlinks       # write back
        num_ptlinks = self.open_url_tree(user)
        logger.debug('Cyberhome未読メール: 解析開始')
        self.appdict.data['log'][user['name']].append(f'Not visited before: [{sum(num_ptlinks)}]')
        logger.info('Cyberhome未読メール: 解析開始')
        # ==============================
        wait.until(EC.visibility_of_element_located((By.ID, "menu_mail_inbox_unread")))
        wait.until(EC.element_to_be_clickable((By.ID, "menu_mail_inbox_unread")))
        driver.find_element(By.ID,"menu_mail_inbox_unread").click()
        mail_table = driver.find_element(By.ID,r"mail_list_tbody")
        mails = mail_table.find_elements(By.TAG_NAME,r"tr")
		#
        self.appdict.data['log'][user['name']].append(f'Mails: {len(mails)}')
        found_mail = []
        found_link = []
        for mail in mails:
            logger.debug('- 対象メールを確認(件名を取得)')
            # ------------------------------
            targ_subject = mail.find_element(By.XPATH,'td[4]/div/span[1]').text
            logger.debug(f'  --TARGET:{targ_subject}')

            logger.debug('- 対象メールを選択し、画像表示モードに変更')
            # ------------------------------
            mail.find_element(By.XPATH,'td[4]/div/span[1]').click()
            body = driver.find_element(By.ID,'home_content_mail_body')
            for i in range(6):              # Wait mail header update until 3 second.
                time.sleep(0.5)
                mbi_subject = body.find_element(By.ID, "mbi_subject").text
                logger.debug(f'  --{i}:{mbi_subject}')
                if mbi_subject == targ_subject: break
            mbi_from = body.find_element(By.ID, "mbi_from").text
            logger.debug(f'-- >{mbi_from}<')
            
            img_toggle = body.find_elements(By.LINK_TEXT,'画像を表示')
            if len(img_toggle) > 0:
                img_toggle[0].click()
            else:
                logger.debug('- 画像表示モードなし(テキストメール)')

            logger.debug('- メール本文を解析し、ポイント誘導リンクをクリック')
            # ------------------------------
            if re.search(r'info@moppy\.jp>$', mbi_from):
                logger.debug('  - it seems MOPPY\'s mail.')
                pickup_type = 'Moppy'
                links = self.pilot_internal_pickup_url_moppy(mbi_subject, mbi_from)
            elif re.search(r'mailmag@hapitas.jp>', mbi_from):
                pickup_type = 'Hapitas'
                links = self.pilot_internal_pickup_url_hapitas(mbi_subject, mbi_from)
            elif re.search(r'info@sbipoint.jp>', mbi_from):
                pickup_type = 'SBIgroup'
                links = self.pilot_internal_pickup_url_sbigroup(mbi_subject, mbi_from)
            elif re.search(r'mag@pointi.jp>$', mbi_from):
                # logger.debug('  - it seems PointIncome\'s mail.')
                pickup_type = 'PointIncome'
                links = self.pilot_internal_pickup_url_pointincome(mbi_subject, mbi_from)
            elif re.search(r'info-stadium@point-stadium.com>$', mbi_from):
                # logger.debug('  - it seems PointStadium\'s mail.')
                pickup_type = 'PointStadium'
                links = self.pilot_internal_pickup_url_pointstadium(mbi_subject, mbi_from)
            else:
                logger.debug('  - it seems any other mail: suppose as Rakuten.')
                pickup_type = 'Rakuten'
                links = self.pilot_internal_pickup_url_rakuten(mbi_subject, mbi_from)

            if len(links) > 0:
                # linksのURLを保存して、メールに削除マークを付ける。
                if ptlinks.get(pickup_type) is None:
                    ptlinks[pickup_type] = []
                ptlinks[pickup_type].extend(links)
                found_link.extend(links)
                found_mail.append(mail)
                logger.debug(f'-->> {len(links)} link(s) is/are found in this mail.')
            else:
                logger.debug(f'-->> No link is found in this mail.')

        logger.info('Cyberhome未読メール: 解析終了')
        # ------------------------------
        self.appdict.data['ptlinks'][user['name']] = ptlinks

        logger.debug('- 最終表示メールの選択状態を解除')
        # ------------------------------
        ## mailとmails[-1]はどっちが安全？0件のときが危ない？
        if len(mails) > 0:
            mails[-1].find_element(By.XPATH,'td[1]/div/input').click()

        self.appdict.data['log'][user['name']].append(f'-> {len(found_link)} link(s) in {len(found_mail)} mail(s).')

        logger.info('ポイントURL付きメールを削除')
        # ==============================
        num_found = len(found_mail)
        if num_found > 0:
            logger.debug(f'- 対象メールを選択(チェック付与) (#found_mail={num_found})')
            # ------------------------------
            for m in found_mail:
                m.find_element(By.XPATH,'td[1]/div/input').click()
            time.sleep(0.5)
            logger.debug('- チェック済みメールを削除')
            # ------------------------------
            driver.find_element(By.XPATH,       # メニュー展開
                '//*[@id="ml_plus"]/div[4]/div/span'
            ).click()
            driver.find_element(By.XPATH,       # チェック済みメールを削除
                "//li[@onclick='return HomeFn.e_dropdown_mail_delete_checked();']"
            ).click()
            time.sleep(1)
            driver.find_element(By.ID,          # 削除確認ダイアログを確認
                "mail_delete_dialog_ok_button"
            ).click()
            time.sleep(1)
            logger.debug('  - 削除確認ダイアログの表示をチェック')
            wait.until(EC.alert_is_present())
            time.sleep(1)
            self.assertEqual(u"メールをごみ箱に移動しました。", self.close_alert_and_get_its_text())
        else:
            logger.debug(f'- 削除対象メールなし(#found_mail={num_found})')
        self.appdict.data['log'][user['name']].append(f'Deleted mails: {num_found}')

        logger.info('抽出したポイント付きURLを訪問')
        # ==============================
        # メール一覧に対象がなくても一時保存URLが残っていれば処理が必要。
        cnt_OK, cnt_NG, sum_OK, sum_NG = [0, 0, 0, 0]
        for i in self.appdict.data['sites']:
            cnt_OK, cnt_NG = self.pilot_internal_visit(user['name'], i[0], i[1])
            sum_OK += cnt_OK
            sum_NG += cnt_NG
        self.appdict.data['log'][user['name']].append(f'Visited: o={sum_OK} / x={sum_NG}')

        num_ptlinks = self.open_url_tree(user)
        self.appdict.data['log'][user['name']].append(f'Cannot visit: {sum(num_ptlinks)}.')

        logger.info(f'アクセスできなかったURLを一時保存(次回処理)')
        # ==============================
        logger.debug(f'- 一時保留URL={sum_NG}')
        logger.debug(f'  - ptlinks={self.appdict.data["ptlinks"]}')
        fname = str(self.appdict.name).lower()
        with open(f'{fname}_remain.yaml', 'w', encoding='utf-8') as f:
            #TODO: last_done.yamlで手当できないか？
            yaml.dump(self.appdict.data['ptlinks'], f, default_flow_style=False, allow_unicode=True)
        self.appdict.data['log'][user['name']].append(f'Non-visited: {sum_NG} link(s).')

        self.pilot_result.append([user['name'],self.appdict.data['log'][user['name']]])
        logger.debug('@@pilot_internal: END')

if __name__ == "__main__":
    import pprint
    try:
        App = CyberhomeMail()
        App.prepare()
        App.pilot('CyberhomeMail', 'CyberhomeMail')
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
