from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import SessionNotCreatedException
from webdrivermanager import ChromeDriverManager
from logging import DEBUG, INFO, WARNING
import pprint
from pathlib import Path
import sys
import time
import datetime
import random
from logutils import logger
import yaml
from logutils import mailreporter



class RWebSearch():
    """ """
    MODULE_NAME = 'RWebSearch'

    def __init__(self):
        self.driver = None
        self.wait = None
        self.pilot_record = []
        self.logger = logger.Logger(self.MODULE_NAME, clevel=DEBUG, flevel=DEBUG)
        try:
            with open('last_done.yaml', 'r', encoding='utf-8') as f:
                self.last_done = yaml.safe_load(f)
        except:
            self.last_done = {}
        try:
            with open('settings.yaml', 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except:
            self.config = {}
        users = self.config.get('users', {})
        self.users = users.get('Rakuten',[])
        random.shuffle(self.users)
        self.pilot_record = []
        self.reporter = mailreporter.MailReporter(r'smtpconf.yaml', 'RWebSearch')

    def setup(self):
        """ """
        logger = self.logger

        if self.driver is not None:
            logger.debug(f"  setup(): self.driver is already setted up.  Do nothing.")
            return self.driver

        msg = r''
        options = Options()
        # 楽天ウェブ検索をインポート
        options.add_extension("4.648_0.crx")
        # 「Chrome は自動テスト ソフトウェアによって制御されています 」のメニューバーの非表示
        # options.add_argument("--disable-infobars")
        options.add_argument("disable-infobars")
        # 画像非表示
        options.add_argument("--blink-settings=imagesEnabled=false")
        # pprint.pprint(options.extensions)  # dir(options))
        try:
            cdm = ChromeDriverManager()
            ld_webdriver = self.last_done.get('WebDriver',{})
            logger.debug(f"  -- last_done.webdriver: {pprint.pformat(ld_webdriver)}")
            previous = ld_webdriver.get('Chrome',['',datetime.datetime.min])
            logger.debug(f"  -- get_download_path() == Re-use driver.")
            # _, filename = cdm.get_download_url()
            # dl_path = cdm.get_download_path()
            driver_path = previous[0]

            logger.debug(f"  driver_path: {driver_path}")
            self.driver = webdriver.Chrome(driver_path, options=options)
        except SessionNotCreatedException as e:
            """
            TODO:　Chromeのバージョンアップが考えられるのでWebDriverのバージョンアップを試みる。
            """
            msg += f" -- {type(e)}: {e.msg}\n"
            msg += f"!! Maybe unmatch Chrome vs chromewebdriver. <{sys._getframe().f_lineno}@{__file__}>.  Exit.\n"
            msg += "\n"
            msg += f"   And try to update chrome driver...\n"

            try:
                logger.debug(f"  -- download_and_install() == Try to update driver")
                driver_path = cdm.download_and_install()[0]
                ld_webdriver['Chrome'] = [driver_path,datetime.datetime.now()]
                self.last_done['WebDriver'] = ld_webdriver
                logger.debug(f"  driver_path: {driver_path}")
                self.driver = webdriver.Chrome(driver_path, options=options)
            except Exception as e:
                # msg += f" -- {type(e)}: {e.msg}\n"
                msg += f"!! Cannot update ChromeDriver. <{sys._getframe().f_lineno}@{__file__}>.  Exit.\n"
                msg += "\n"
                raise e
        except WebDriverException as e:
            msg += f" -- {type(e)}: {e.msg}\n"
            msg += f"!! Cannot instantiate WebDriver<{sys._getframe().f_lineno}@{__file__}>.  Exit.\n"
            msg += "\n"
        except Exception as e:
            msg += f" -- Ex={type(e)}: {'No message.' if e.args is None else e.args}\n"
            msg += "\n"
        finally:
            if self.driver is None:
                for alerter in [logger, self.reporter]:
                    alerter.critical(msg)

        self.driver.implicitly_wait(20)
        logger.debug(f'  -- {self.driver}')
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver

    def realtime_words(self):
        """ ヤフーリアルタイム検索よりワード生成 """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        driver.get("http://search.yahoo.co.jp/realtime")
        time.sleep(1)
        # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.que_3 > a")))
        # word_list = driver.find_elements_by_css_selector("p.que_3 > a")
        #body > div.Top > article > section > ol:nth-child(1) > li:nth-child(1) > a
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#body > div.Top > article > section")))
        word_list = driver.find_elements_by_css_selector("#body > div.Top > article > section > ol > li > a")
        words = [a.text for a in word_list]
        # word_list = driver.find_elements_by_css_selector("#body > div.Top > article > section > ol:nth-child(2) > a")
        # words.extend( [a.text for a in word_list] ) 
        logger.debug(words)
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return words

    def pilot_logout(self):
        driver = self.driver
        logger = self.logger
        wait = self.wait

        # # logout_link = driver.find_elements_by_class_name('rakuten-user-logout')
        # logout_link = driver.find_elements_by_xpath(
        #     '//*[@id="rakuten-membership"]/div/div[2]/div[2]/div/div[1]/div[2]/div'
        # )
        # logout_link_num = len(logout_link)
        # logger.debug(f'  -- Num: {logout_link_num} <- XPATH: (omitted ... its too long)')
        # if logout_link_num > 0:
        #     logout_link[0].find_elements_by_xpath('a').click()
        # else:
        #     logger.error(f'  !! No logout link found.')
        # return logout_link_num

        ### 楽天競馬のオートパイロットからパクリ
        driver.get("https://keiba.rakuten.co.jp/")
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.glonavmain')))
        result = self.is_element_present(By.LINK_TEXT, u"ログアウト")
        logger.debug(f"  -- LINK_TEXT[ログアウト] exists? {result}")
        if result is True:
            logger.debug(f"  -- Try to click ログアウト link.")
            driver.find_element_by_link_text(u"ログアウト").click()
        else:
            logger.debug(f"  -- Do nothing and exit.")
        return result

    def pilot_login(self, user):
        """ 楽天ウェブサーチにログイン """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        logger.info("  Try to login 楽天ウェブサーチ")
        driver.get("https://websearch.rakuten.co.jp/Web?qt=楽天")
        time.sleep(1)
        # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.login-link"))).click()
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "ログイン")))
        driver.find_element_by_link_text(r"ログイン").click()
        rakutenID = wait.until(EC.visibility_of_element_located((By.NAME, "u")))
        rakutenID.send_keys(user['id'])
        rakutenPass = wait.until(EC.visibility_of_element_located((By.NAME, "p")))
        rakutenPass.send_keys(user['pw'])
        logger.debug("  -- Click SUBMIT.")
        wait.until(EC.visibility_of_element_located((By.NAME, "submit"))).click()

    def search_rws(self, words):
        """ 楽天ウェブサーチの実行 """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        wait.until(EC.visibility_of_element_located((By.ID, "srchformtxt_qt"))).clear()
        logger.info("  検索開始")
        random.shuffle(words)
        for word in words:
            logger.info(f"  -- Keyword: {word}")
            logger.debug(f'   (Wainting for (By.ID, "srchformtxt_qt")')
            kwarea = wait.until(EC.visibility_of_element_located((By.ID, "srchformtxt_qt")))
            kwarea.clear()
            kwarea.send_keys(word, Keys.ENTER)
            time.sleep(3)
            logger.debug(f'   (Wainting for (By.CLASS_NAME, "progress-message")')
            mes = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "progress-message"))).text
            logger.debug(f'   {mes}')
            # logger.debug(f'   (Wainting for (By.ID, "curr-kuchisu-count")')
            # 検索画面のレイアウトが２種類できたみたい。 @20200418
            # progress-messageの表示確認が取れていれば、口数情報の取得位置を変えるだけでよさそう。
            # objects = driver.find_elements_by_id("curr-kuchisu-count")
            objects = driver.find_elements_by_xpath('//*[@id="wrapper"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')
            if len(objects) > 0:
                logger.debug(f"   Found: (By.XPATH, '//*[@id=\"wrapper\"]/header/div/div/div[2]/div[2]/div[2]/div/div[1]/span[2]/span/em')")
                cnt = objects[0].text
            else:
                logger.debug(f"   Found: (By.ID, 'curr-kuchisu-count')")
                cnt = driver.find_element_by_id("curr-kuchisu-count").text
            logger.debug(f'   検索実績: {cnt} 件目')
            """
            #ページクリック用：利用するかは各自にお任せします
            int = random.randrange(10)
            pageLinks = driver.find_elements_by_class_name("os-window")
            actions = ActionChains(driver)
            actions.move_to_element(pageLinks[int])
            actions.perform()
            pageLinks[int].click()
            driver.back()
            """
            if (int(cnt) >= 30):
                logger.info(f"  本日実績が30口を超えました[{cnt}]")
                break
        logger.info(f'  検索終了: 本日実績は{cnt}件まで進んでいます')
        return int(cnt)

    def pilot(self):
        """ オートパイロットの実行 """
        logger = self.logger
        config = self.config

        logger.debug(f"Read user & service information form yaml.")
        # ==============================
        # Get user information
        users = config.get('users',{})
        users_rakuten = users.get('Rakuten',[])
        # Get service information
        svcs = config.get('services',{})
        svcs_rws = svcs.get('RWebSearch',[])
        if len(users_rakuten) * len(svcs_rws) == 0:
            self.logger.warn(f"No user({len(users_rakuten)}) or service({len(svcs_rws)}) is found.  exit.")
            return
        last_dones = self.last_done.get('RWebSearch',{})

        # num_users = len(self.users)
        # self.logger.info(f"ユーザ数（設定ファイル内）: {num_users}")
        # if num_users <= 0:
        #     logger.error(f'実行対象ユーザが登録されていません')
        #     # self.tearDown()
        #     return
        words = None
        need_report = 0
        today = datetime.datetime.strptime(
            datetime.datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "%Y-%m-%d 00:00:00",
        )
        for user in users_rakuten:
            if user['name'] not in svcs_rws:
                logger.info(f"- User {user['name']} do not use this service.  Skip.")
                continue

            need_report += 1
            # 実行記録確認
            who = user['id']
            last_done = last_dones.get(who, datetime.datetime.min)
            logger.debug(f" {who}: today={today} vs last={last_done}")
            if today < last_done:
                msg = f"{user['name']}({who}): Already done today.  SKIP."
                need_report -= 1     # メール報告不要
                logger.info(msg)
                self.pilot_record.append(msg)
                continue

            # 実処理実行
            # wk = {}
            # for key in ('id', 'name'):
            #     wk[key] = user.get(key,'')
            wk = {k:v for (k,v) in user.items() if k in ('name','id')}
            logger.info(f" Rakuten Web Search starts for {wk}")
            try:
                msg = 'Not processed normally.'
                if self.setup():
                    if words is None:
                        words = self.realtime_words()
                        logger.info(f'-- collected words: {len(words)} itme(s).')
                    if len(words) > 0:
                        self.pilot_login(user)
                        cnt = self.search_rws(words)
                        if cnt >= 30:
                            last_dones[who] = datetime.datetime.now()
                        logger.debug(f"  -- Porcessed {cnt} item(s).")
                        msg = f'Porcessed {cnt} item(s).'
                        res = self.pilot_logout()
                        logger.debug(f"  -- logout with status=<{res}> (return value is not noteworthy)")
                        msg += f'  ...and logout status=<{res}>'
                    else:
                        msg = 'There is no words to search.  SKIP.'
                else:
                    msg = 'Webdriver cannot set up.  SKIP.'
            except Exception as e:
                wk = f'Caught EXCEPTION: {type(e)}!!'
                logger.error(wk)
                msg += wk
            finally:
                self.pilot_record.append(f'{user["name"]}: {msg}')
        logger.info(f"実行記録を保存")
        # ==============================
        try:
            self.last_done['RWebSearch'] = last_dones
            with open('last_done.yaml', 'w', encoding='utf-8') as f:
                logger.debug(f" -- {self.last_done}")
                f.write(yaml.dump(self.last_done))
                logger.info(f" 実施記録を保存しました")
        except Exception as e:
            logger.warn(f" 実施記録を保存できませんでした(ignore)")
        logger.info(f"全処理を完了")
        # ==============================
        logger.info(f'Result: {self.pilot_record}')
        if self.pilot_record != [] and need_report > 0:
            report = sorted(self.pilot_record, key=lambda x: x[0])
            self.reporter.critical(f" 処理結果: {pprint.pformat(report,width=80)}")

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def tearDown(self):
        if self.driver is not None:
            self.driver.quit()


if __name__ == "__main__":
    App = RWebSearch()
    App.pilot()
    App.tearDown()
