import time
import re
import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import yaml
import RPAbase.RakutenBase
import logutils.AppDict

class MailDePoint(RPAbase.RakutenBase.RakutenBase):
    # def pilot_setup(self):
    #     super.pilot_setup(name)
    def __init__(self):
        self.super = super(MailDePoint, self)
        self.super.__init__()
        self.appdict = logutils.AppDict.AppDict
        self.appdict.setup(
            r'MailDePoint', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        self.super.prepare(self.appdict.name)
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        ### Obsoleted
        # options.add_argument(r'--disable-infobars')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        super(MailDePoint, self).pilot_setup(options)

    def pilot_internal1(self):
        """
        Pilot for parse mail list.
        メールボックス内の未読一覧から、未読メールの情報を収集する
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger

        try:
            driver.get("https://member.pointmail.rakuten.co.jp/box")
            driver.find_element_by_link_text(u"メールボックス").click()
            driver.find_element_by_link_text("未読").click()
            logger.debug(f'  wait for visibility_of_element_located: CLASS_NAME:mailboxBox')
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"mailboxBox")))

            mailbox = driver.find_element_by_class_name("mailboxBox")
            mails = mailbox.find_elements_by_xpath("ul/li")
            logger.debug(f'  Found {len(mails)} mail(s) in mailbox.')
            point_contents = []
            for mail in mails:
                class_value = mail.get_attribute("class")
                if class_value == "teamSiteSubject":
                    # 広告メール以外はスキップする。
                    logger.debug(f'  - 広告メール(class="teamSiteSubject"): SKIP.')
                    continue
                else:
                    # 広告以外の未読メールのはず
                    divs = mail.find_elements_by_xpath("div")
                    if len(divs) == 0:
                        # リンク情報なしのためスキップ。おそらく未読メール残が０件の状態。
                        logger.debug(f'  - メール本体が存在しない: おそらく未読メールなし状態')
                        continue
                    subj = divs[1].find_element_by_xpath("a/p").text
                    href = divs[1].find_element_by_xpath("a").get_attribute(r'href')
                    wk = [class_value, subj, href]
                    logger.debug(f'  - Found target: {wk}')
                    point_contents.append(wk)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Parsing mail list: {type(e)} {e.args}')

        logger.debug(f'  => Found {len(point_contents)} effective mail(s).')
        logger.debug(pprint.pformat(point_contents))

        return point_contents
    
    def pilot_internal2(self,point_contents):
        """
        pilot to collect urls form each mail body.
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        re_url = re.compile(r'^https?://pmrd\.')
        point_urls = []
        #--------------------
        logger.info(f' Revive previous remain list.')
        #--------------------
        try:
            with open(appdict.wkfile(substr=r'_remain', suffix=r'yaml'),
                    r'r', encoding=r'utf-8') as f:
                point_urls = yaml.safe_load(f)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Reviving previous remain list: {type(e)} {e.args}')

        #--------------------
        logger.info(f' Collect newly arrived mails.')
        #--------------------
        try:
            for cont in point_contents:
                title = cont[1]
                url = cont[2]

                logger.debug(f" Open url: {url}")
                driver.get(url)
                links = driver.find_elements_by_xpath('//*[@id="mailFrame"]//*/a')
                logger.debug(f" Collected links in mail body: {len(links)}")
                if len(links) > 0:
                    urls = []
                    for link in links:
                        href = link.get_attribute(r'href')
                        logger.debug(f" - Check: {href}")
                        if re_url.findall(href):
                            logger.debug(f" -- Regex matches.")
                            if href not in urls:
                                logger.debug(f" -- Discover new point url.  Add to result list.")
                                urls.append(href)
                            else:
                                logger.debug(f" -- Already in result list.  Ignore.")
                        else:
                            logger.debug(f" -- Regex not matches.  Skip.")
                    result = [len(links), title, [len(urls),urls]]
                else:
                    result = [0, title, [0,[r'None']]]
                logger.debug(f" - Result: {result}")
                point_urls.append(result)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Collect newly arrived mails: {type(e)} {e.args}')
            logger.debug(f' Some points will be lost.')

        logger.debug(f'  => Collect point urls form {len(point_urls)} effective mail(s).')
        logger.debug(pprint.pformat(point_urls))
        return point_urls

    def pilot_internal3(self, point_urls):
        """
        pilot to get point from collected urls.
        """
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        unvisited_urls = []
        for point_item in point_urls:
            subj = point_item[1]
            urls = point_item[2]
            if urls[0] > 0:
                logger.info(f" Processing mail: {subj}.")
                wk = [urls[1]] if type(urls[1]) == str else urls[1]
                try:
                    for url in wk:
                        logger.debug(f"  Try to get url: {url}.")
                        driver.get(url)
                    self.pilot_result.append(f'Success: {len(urls)} url(s) in {subj}.')
                except Exception as e:
                    logger.error(f" {type(e)}: {e.args})")
                    # ひとつでもURL訪問に失敗したら次回へ先送り
                    logger.warn(f" - To visit {url}, something wrong is occured.  snooz.")
                    unvisited_urls.append(point_item)

        if unvisited_urls != []:
            logger.warning("!! Some urls cannot be visited normally.  Try to save urls for next challenge.")
            logger.debug(
                pprint.pformat(unvisited_urls)
            )

        try:
            with open(appdict.wkfile(substr=r'_remain', suffix=r'yaml'),
                    r'w', encoding=r'utf-8') as f:
                yaml.dump(unvisited_urls, f)
        except Exception as e:
            logger.error(f' Caught Ex(Ignore): Save remain url list: {type(e)} {e.args}')
            logger.debug(f' Some url list(s) may be lost.')
        
        return unvisited_urls

    def pilot(self):
        self.pilot_setup()

        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict

        try:
            rakuten_users = self.config.get(r'Rakuten', [])
            target_users = self.config.get(appdict.name, [])
            for user in rakuten_users:
                if user['id'] not in target_users:
                    # 実行対象外ユーザはスキップ
                    continue
                # ユーザ情報のロギング
                wk = user.copy()
                wk.pop('pw')
                logger.debug(f" Processing for user: {wk}")
                if self.pilot_login(user):
                    # parse mail, and get points
                    contents = self.pilot_internal1()
                    urls = self.pilot_internal2(contents)
                    results = self.pilot_internal3(urls)
                    logger.info(f'There is/are {len(self.pilot_result)} url(s) which was successfully visited.')
                    logger.info(f'And, there is/are {len(results)} url(s) which must be visited later.')
                    self.pilot_logout()
                else:
                    logger.error(f'Login failed for user(SKIP): <{user["id"]}>')
        except Exception as e:
            logger.error(f"Caught exception: {type(e)} {e.args}")


if __name__ == "__main__":
    App = MailDePoint()
    App.prepare()
    App.pilot()
    App.tearDown()
