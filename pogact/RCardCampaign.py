# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import logutils.AppDict
import time
import re
import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import yaml
from RPAbase.RCardBase import RCardBase
from logutils.AppDict import AppDict


class RCardCampaign(RCardBase):
    """
    """

    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'RCardCampaign', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        super().prepare(self.appdict.name, '★楽天カード: クリックしてポイント')
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        # options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return super().pilot_setup(options)

    def visit_and_close(self, cnt, item):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(f'  @@visit_and_close(): START')
        logger.debug(f'    ({cnt}, {"/".join(item.text.splitlines())})')

        # ポイント獲得リンクの確認: URLではなくonclickリンクなので注意
        links = item.find_elements_by_xpath("div[2]/div/a")
        logger.debug(f'  - links:[{len(links)}]')
        url = links[0].get_attribute("onclick")
        logger.debug(f'  -- url  of link:[{url}]')
        title = links[1].text
        logger.debug(f'  -- text of link:[{title}]')
        # click() == point get
        links[0].click()
        time.sleep(0.5)
        # Wait until new page is completely displayed.
        logger.debug(f'  driver.switch_to.window([1]:{driver.window_handles[1]})')
        driver.switch_to.window(driver.window_handles[1])
        logger.debug(f'  wait.until(EC.presence_of_all_elements_located)')
        wait.until(EC.presence_of_all_elements_located)
        logger.debug(f'  wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME,"body")))')
        wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME,"body")))
        url = driver.current_url
        logger.debug(f'  - Visited url: >{url}<.')
        time.sleep(0.8)
        # Then, close new page and back to previos.
        logger.debug(f'  --- Then, close new page, and back to previous page.')
        driver.close()
        logger.debug(f'  driver.switch_to.window([0]:{driver.window_handles[0]})')
        driver.switch_to.window(driver.window_handles[0])

        logger.debug(f'  @@visit_and_close(): END')
        return title  # url

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(f'  @@pilot_internal: START')

        xpath_of_unaquired_item = lambda cnt: f'//span[@id="topArea"]/div[{cnt}]'
        xpath_of_unaquired_symbol = lambda cnt: f'//span[@id="topArea"]/div[{cnt}]/div/p/img'

        urls = []
        try:
            # Wait page top
            driver.get("https://www.rakuten-card.co.jp/e-navi/members/index.xhtml")
            logger.debug(f'wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.rce-l-wrap.is-grey.rce-main")))')
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.rce-l-wrap.is-grey.rce-main")))

            # Move to target page
            driver.find_element_by_partial_link_text("クリックしてポイント").click()
            logger.debug(f' - wait.until(EC.visibility_of_element_located((By.ID, "contentsArea")))')
            wait.until(EC.visibility_of_element_located((By.ID, "contentsArea")))

            # 未獲得ポイント
            if self.is_element_present(By.ID,"procurablePoint"):
                unaquired = driver.find_element_by_id("procurablePoint").text
                logger.info(f' 未獲得ポイント数: [{unaquired}]')
                # 無限ループ
                cnt = 1
                while True:
                    logger.debug(f'-- Loop start: cnt={cnt}')
                    top_area = driver.find_element_by_id("topArea")
                    items = top_area.find_elements_by_xpath("div")
                    logger.debug(f'items: [{len(items)}]')
                    found = False
                    # for item in items:
                    #     # 未取得マークの確認
                    #     click_button = item.find_elements_by_xpath("div/p/img")
                    #     if len(click_button) > 0:
                    #         found = True
                    #         cnt += 1
                    #         logger.debug(f' Unaquired link is found.  [found={found},cnt={cnt}]')
                    #         urls.append(self.visit_and_close(cnt,item))
                    #         break
                    logger.debug(f'  - XPATH={xpath_of_unaquired_item(cnt)}')
                    if self.is_element_present(By.XPATH,xpath_of_unaquired_item(cnt)):
                        item = driver.find_element_by_xpath(xpath_of_unaquired_item(cnt))
                        if self.is_element_present(By.XPATH,xpath_of_unaquired_symbol(cnt)):
                            # unacquired item is found.
                            found = True
                            logger.debug(f' Unaquired link is found.  [found={found},cnt={cnt}]')
                            urls.append(self.visit_and_close(cnt-1,item))
                            cnt += 1

                    # 有効なリンクが見つからない or 上限到達で中断
                    # 練習中は99発で切る
                    if found == False or cnt > 99:
                        logger.debug(f'  Search {"success" if found else "failure"}, or Reach 100 urls[{cnt}].')
                        break
                    # リフレッシュして繰り返す
                    logger.debug(f'  Loop end and REFRESH: {driver.current_url}')
                    driver.refresh()
                    logger.debug(f' - wait.until(EC.visibility_of_element_located((By.ID, "contentsArea")))')
                    wait.until(EC.visibility_of_element_located((By.ID, "contentsArea")))
            else:
                # 獲得ポイント数非表示＝獲得対象なし
                unaquired = "0"
        except Exception as e:
            urls.append(f'Caught Exception: {type(e)} {e.args if hasattr(e,"args") else str(e)}')
        finally:
            self.pilot_result.append( [account.get("name","Unknown"), unaquired, (len(urls), urls) ] )

        logger.debug(f'  @@pilot_internal: END')


if __name__ == "__main__":
    try:
        from operator import itemgetter
        App = RCardCampaign()
        App.prepare()
        App.pilot()
        # pprint.pprint(App.pilot_result, width=40)
        App.pilot_result.sort(key=itemgetter(0))
        # print(App.pilot_result)
        App.report(
            pprint.pformat(App.pilot_result, width=40)
        )
        App.tearDown()
    except Exception as e:
        print(f'Caught Exception: {type(e)} {e.args if hasattr(e,"args") else str(e)}')
        if App.driver is not None:
            App.driver.quit()
