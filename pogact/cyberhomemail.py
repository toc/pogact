# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
# import unittest, 
import time, re
from bs4 import BeautifulSoup
import lxml
import yaml
import pprint
import logutils.AppDict
import logutils.mailreporter
import RPAbase.CyberhomeBase

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
            r'CyberhomeMail', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )
        self.reporter = logutils.mailreporter.MailReporter(r'smtpconf.yaml', self.appdict.name)

    def prepare(self):
        """
        Prepare something before execute browser.
        1. Read setting file(s).
        1. Update webdriver, if needed.
        1. Prepare work file/folder, and so on.
        """
        super().prepare(self.appdict.name)
        try:
            fname = str(self.appdict.name).lower()
            with open(f'{fname}_remain.yaml', 'r', encoding='utf-8') as f:
                self.appdict.data['ptlinks'] = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f' Caught Ex(Ignore): Reviving previous remain list: {type(e)} {e.args}')
            self.appdict.data['ptlinks'] = []

    def pilot_setup(self):
        """
        Execute web browser, and set up for auto-pilot.
        1. Setting up web browser: OPTIONS, EXTENTIONS, ...
        1. Execute web browser.
        1. Fetch some information(s) with web browser.
        """
        options = Options()
        options.add_argument(r'--headless')
        # イメージボタンが多用されているため、img表示は必要
        # options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        return super().pilot_setup(options)
    
    def pilot_internal3(self,name):
        """
        楽天にログインした状態で収集したURL(link)を訪問する。
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(' @@pilot_internal3:START')

        logger.info(' 楽天にログイン')
        # ==============================
        logger.debug(' - 楽天ユーザ情報を取得')
        # ------------------------------
        users_rakuten = self.config.get('users',{}).get('Rakuten',{})
        for user in users_rakuten:
            if user['name'] == name:
                break

        logger.debug(' - 楽天ログインページにアクセス')
        # ------------------------------
        driver.get("https://grp01.id.rakuten.co.jp/rms/nid/vc?__event=login&service_id=top")
        logger.debug(f'  --wait.until visibility_of_element_located((By.ID,"loginInner_u"))')
        wait.until(EC.visibility_of_element_located((By.ID,'loginInner_u')))
        driver.find_element_by_id("loginInner_u").clear()
        driver.find_element_by_id("loginInner_u").send_keys(user['id'])
        driver.find_element_by_id("loginInner_p").clear()
        driver.find_element_by_id("loginInner_p").send_keys(user['pw'])
        driver.find_element_by_name("submit").click()

        logger.info(' ポイントURLに順次アクセス')
        # ==============================
        not_visited = []
        num_ptlinks = len(appdict.data['ptlinks'])
        total_count = 0
        for link in appdict.data['ptlinks']:
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
                logger.debug(f'  -- exception: {type(e)} {e.args}')
                not_visited.append(link)
        logger.debug(f'  -- アクセス結果: Total={total_count}, NG={len(not_visited)}')
        appdict.data['ptlinks'] = not_visited

        logger.debug(' @@pilot_internal3:END')


    def pilot(self):
        driver, wait = self.pilot_setup()
        logger = self.logger
        logger.debug('@@pilot:START')

        logger.info('Cyberhomeメールにログイン')
        # ==============================
        user = self.config.get('users',{}).get('CyberhomeMail',{})
        logger.debug(f' - user: >{user["id"]}<')
        self.pilot_login(user)
        logger.debug(f' --wait.until element_to_be_clickable((By.ID,r"menu_mail_inbox_unread"))')
        wait.until(EC.element_to_be_clickable((By.ID,r"menu_mail_inbox_unread")))

        logger.info('Cyberhome未読メール一覧を取得')
        # ==============================
        driver.find_element_by_id("menu_mail_inbox_unread").click()

        mail_table = driver.find_element_by_id(r"mail_list_tbody")
        mails = mail_table.find_elements_by_tag_name(r"tr")
        self.pilot_result.append(f'Cyberhome未読メール一覧を取得: {len(mails)}')

        logger.info('Cyberhome未読メールを順次解析')
        # ==============================
        found_mail = []
        for mail in mails:
            logger.debug('- 対象メールを確認(件名を取得)')
            # ------------------------------
            subject = mail.find_element_by_xpath('td[4]/div/span[1]').text
            logger.debug(f'--{subject}')

            logger.debug('- 対象メールを選択し、画像表示モードに変更')
            # ------------------------------
            mail.find_element_by_xpath('td[4]/div/span[1]').click()
            body = driver.find_element_by_id('home_content_mail_body')
            img_toggle = body.find_elements_by_link_text('画像を表示')

            if len(img_toggle) > 0:
                img_toggle[0].click()

                logger.debug('- メール本文を解析し、ポイント誘導リンクをクリック')
                # ------------------------------
                soup = BeautifulSoup(driver.page_source,"lxml")
                lists = soup.select("a img")        # a内に子タグとしてimgが存在するものを抽出
                found = False
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
                        found = True
                        links.append(l.parent.get("href"))
                        logger.debug(f'--FOUND:img src={wk}')
                        logger.debug(f'--STORED href={l.parent.get("href")}')

                if found:
                    # linksのURLを訪問または保存して、メールに削除マークを付ける。
                    self.appdict.data['ptlinks'].extend(links)
                    found_mail.append(mail)
                    logger.debug(f'-->> {len(links)} link(s) is/are found in this mail.')
                else:
                    logger.debug(f'-->> No link is found in this mail.')
            else:
                logger.debug('- 画像表示モードなし(テキストメール): SKIP')
        found_link = self.appdict.data["ptlinks"].copy()

        logger.debug('- 最終表示メールの選択状態を解除')
        # ------------------------------
        ## mailとmails[-1]はどっちが安全？0件のときが危ない？
        if len(mails) > 0:
            mails[-1].find_element_by_xpath('td[1]/div/input').click()

        self.pilot_result.append(f'Cyberhome未読メールを順次解析: {len(found_link)} link(s) in {len(found_mail)} mail(s).')

        logger.info('ポイントURL付きメールを削除')
        # ==============================
        num_found = len(found_mail)
        if num_found > 0:
            logger.debug(f'- 対象メールを選択(チェック付与) (#found_mail={num_found})')
            # ------------------------------
            for m in found_mail:
                m.find_element_by_xpath('td[1]/div/input').click()
            time.sleep(2)
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
            # self.assertEqual(u"メールをごみ箱に移動しました。", self.close_alert_and_get_its_text())
        else:
            logger.debug(f'- 削除対象メールなし(#found_mail={num_found})')
        self.pilot_result.append(f'ポイントURL付きメールを削除: {num_found} mail(s).')

        logger.info('抽出したポイント付きURLを訪問')
        # ==============================
        # メール一覧に対象がなくても一時保存URLが残っていれば処理が必要。
        if len(self.appdict.data['ptlinks']) > 0:
            self.pilot_internal3(user['name'])
        else:
            logger.debug('- 処理対象URLなし:　SKIP')
        self.pilot_result.append(f'抽出したポイント付きURLを訪問: try={len(found_link)} / NG={len(self.appdict.data["ptlinks"])}')

        logger.info(f'アクセスできなかったURLを一時保存(次回処理)')
        # ==============================
        logger.debug(f'- 一時保留URL={len(self.appdict.data["ptlinks"])}')
        fname = str(self.appdict.name).lower()
        with open(f'{fname}_remain.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(self.appdict.data['ptlinks'],f)
        self.pilot_result.append(f'Save not-visited URLs. {len(self.appdict.data["ptlinks"])} link(s).')

        logger.info(f"全処理を完了")
        # ==============================
        self.tearDown()
        
        if self.pilot_result != []:
            self.reporter.report(pprint.pformat(self.pilot_result, width=72))
            logger.debug(f" 処理結果を　Mailreporter　経由で送信しました")

        logger.debug('@@pilot: END')

if __name__ == "__main__":
    try:
        App = CyberhomeMail()
        App.prepare()
        App.pilot()
    except Exception as e:
        print(e.args)
        if App:
            if App.driver:
                App.driver.quit()
