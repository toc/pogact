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
from bs4 import BeautifulSoup
import lxml
import yaml
import logutils.AppDict
import RPAbase.CyberhomeBase
import RPAbase.RakutenBase
import RPAbase.MoppyBase
import RPAbase.HapitasBase

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
        ### Rakuten
        wk = RPAbase.RakutenBase.RakutenBase()
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


    def pilot_internal_pickup_url_moppy(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - moppyを想定してメール本文を解析')
        # ------------------------------
        links = []

        soup = BeautifulSoup(driver.page_source,"lxml")
        lists = soup.select("a")
        regex = re.compile(r'^https://pc.moppy.jp/clc/\?clc_tag=\S+$', re.A)
        for l in lists:
            wk = l.get("href")
            if regex.match(wk):
                links.append(wk)
                logger.debug(f'--FOUND:a href={wk}')

        # URLリストを返却、空リストなら対象なし(楽天メール外？)
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

        # URLリストを返却、空リストなら対象なし(楽天メール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def pilot_internal_pickup_url_rakuten(self, subj, fr):
        driver = self.driver
        logger = self.logger

        logger.debug('  - 楽天Mail de pointを想定してメール本文を解析')
        # ------------------------------
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
                ):
                links.append(l.parent.get("href"))
                logger.debug(f'--FOUND:img src={wk}')
                logger.debug(f'--STORED href={l.parent.get("href")}')

        # URLリストを返却、空リストなら対象なし(楽天メール外？)
        logger.debug(f'    解析終了: 該当URL数[{len(links)}]')
        return links


    def pilot_internal(self, user):
        driver = self.driver
        wati = self.wait
        logger = self.logger
        logger.debug('@@pilot_internal:START')

        logger.info('Cyberhome未読メール: 解析開始')
        # ==============================
        if self.appdict.data.get('log') is None:
            self.appdict.data['log'] = {}
        self.appdict.data['log'][user['name']] = []
        driver.find_element_by_id("menu_mail_inbox_unread").click()
        mail_table = driver.find_element_by_id(r"mail_list_tbody")
        mails = mail_table.find_elements_by_tag_name(r"tr")
        self.appdict.data['log'][user['name']].append(f'Unread mails: {len(mails)}')

        ptlinks = self.appdict.data['ptlinks'].get(user['name'],{})
        found_mail = []
        found_link = []
        for mail in mails:
            logger.debug('- 対象メールを確認(件名を取得)')
            # ------------------------------
            targ_subject = mail.find_element_by_xpath('td[4]/div/span[1]').text
            logger.debug(f'  --TARGET:{targ_subject}')

            logger.debug('- 対象メールを選択し、画像表示モードに変更')
            # ------------------------------
            mail.find_element_by_xpath('td[4]/div/span[1]').click()
            body = driver.find_element_by_id('home_content_mail_body')
            for i in range(6):              # Wait mail header update until 3 second.
                time.sleep(0.5)
                mbi_subject = body.find_element(By.ID, "mbi_subject").text
                logger.debug(f'  --{i}:{mbi_subject}')
                if mbi_subject == targ_subject: break
            mbi_from = body.find_element(By.ID, "mbi_from").text
            logger.debug(f'-- >{mbi_from}<')
            
            img_toggle = body.find_elements_by_link_text('画像を表示')
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
            mails[-1].find_element_by_xpath('td[1]/div/input').click()

        self.appdict.data['log'][user['name']].append(f'Analyze mails: {len(found_link)} link(s) in {len(found_mail)} mail(s).')

        logger.info('ポイントURL付きメールを削除')
        # ==============================
        num_found = len(found_mail)
        if num_found > 0:
            logger.debug(f'- 対象メールを選択(チェック付与) (#found_mail={num_found})')
            # ------------------------------
            for m in found_mail:
                m.find_element_by_xpath('td[1]/div/input').click()
            time.sleep(0.5)
            logger.debug('- チェック済みメールを削除')
            # ------------------------------
            driver.find_element_by_xpath(       # メニュー展開
                '//*[@id="ml_plus"]/div[4]/div/span'
            ).click()
            driver.find_element_by_xpath(       # チェック済みメールを削除
                "//li[@onclick='return HomeFn.e_dropdown_mail_delete_checked();']"
            ).click()
            time.sleep(1)
            driver.find_element_by_id(          # 削除確認ダイアログを確認
                "mail_delete_dialog_ok_button"
            ).click()
            time.sleep(1)
            logger.debug('  - 削除確認ダイアログの表示をチェック')
            self.assertEqual(u"メールをごみ箱に移動しました。", self.close_alert_and_get_its_text())
        else:
            logger.debug(f'- 削除対象メールなし(#found_mail={num_found})')
        self.appdict.data['log'][user['name']].append(f'Delete processed mails: {num_found} mail(s).')

        logger.info('抽出したポイント付きURLを訪問')
        # ==============================
        # メール一覧に対象がなくても一時保存URLが残っていれば処理が必要。
        cnt_OK, cnt_NG, sum_OK, sum_NG = [0, 0, 0, 0]
        for i in self.appdict.data['sites']:
            cnt_OK, cnt_NG = self.pilot_internal_visit(user['name'], i[0], i[1])
            sum_OK += cnt_OK
            sum_NG += sum_NG
        self.appdict.data['log'][user['name']].append(f'Visit URLs: OK={sum_OK} / NG={sum_NG}')

        logger.info(f'アクセスできなかったURLを一時保存(次回処理)')
        # ==============================
        logger.debug(f'- 一時保留URL={sum_NG}')
        fname = str(self.appdict.name).lower()
        with open(f'{fname}_remain.yaml', 'w', encoding='utf-8') as f:
            #TODO: last_done.yamlで手当できないか？
            yaml.dump(self.appdict.data['ptlinks'], f, default_flow_style=False, allow_unicode=True)
        self.appdict.data['log'][user['name']].append(f'Save not-visited URLs. {sum_NG} link(s).')

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
            App.driver.quit()
    finally:
        # App.pilot_result.sort(key=itemgetter(0))
        result = App.pilot_result
        if result != []:
            import pprint
            App.report(
                pprint.pformat(result, width=40)
            )
