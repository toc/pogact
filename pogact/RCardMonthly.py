# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from RPAbase.RCardBase import RCardBase
from logutils.AppDict import AppDict


class RCardMonthly(RCardBase):
    def __init__(self):
        super().__init__()
        self.appdict = AppDict
        self.appdict.setup(
            r'RCardMonthly', __file__,
            r'0.1', r'$Rev$', r'Alpha'
        )

    def prepare(self):
        super().prepare(self.appdict.name, '★楽天カード利用額')
        self.logger.info(f"@@@Start {self.appdict.name}({self.appdict.version_string()})")

    def pilot_setup(self):
        options = Options()
        if __debug__ is False:
            options.add_argument(r'--headless')
        options.add_argument(r'--blink-settings=imagesEnabled=false')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        return super(RCardMonthly, self).pilot_setup(options)

    def pilot_internal(self, account):
        driver = self.driver
        wait = self.wait
        logger = self.logger
        appdict = self.appdict
        logger.debug(f'  @@pilot_internal: START')

        bills = []
        try:
            # Wait page top
            # logger.debug(f'wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.ghead.rce-ghead > div.service-bar")))')
            # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#top > div.ghead.rce-ghead > div.service-bar")))

            # get　invoice summary
            # card_info = driver.find_element(By.CSS_SELECTOR,"#top > div.rce-l-wrap.is-grey.rce-main > div > div.rce-billInfo.rf-card.rf-card-square.rf-card-edge > div.rce-contents")
            # summary = card_info.find_element(By.CSS_SELECTOR,"div.rce-columns > div.rce-columns-cell.rce-billInfo-month")
            # bills.append(summary.find_element(By.CSS_SELECTOR,"h3.rf-title-collar.rce-title-belt-first").text)
            # bills.append(summary.find_element(By.CSS_SELECTOR,"table:nth-child(2) > tbody > tr:nth-child(1) > td").text)
            # balance = summary.find_element(By.ID,"parent-balance")
            # divs = balance.find_elements(By.XPATH,"div")
            # for div in divs:
            #     bills.append(div.text)

            ### ポイント実績確認に変更
            # po = (By.LINK_TEXT,"ポイントの詳細")
            # logger.debug(f'wait.until(EC.visibility_of_element_located({po}))')
            # wait.until(EC.visibility_of_element_located(po))
            # driver.find_element(*po).click()
            driver.get("https://point.rakuten.co.jp/?l-id=point_header_top")
            po = (By.LINK_TEXT,"楽天ポイントガイド")
            logger.debug(f'wait.until(EC.visibility_of_element_located({po}))')
            wait.until(EC.visibility_of_element_located(po))
            ###　ポイント情報サマリ
            po = (By.CSS_SELECTOR,".gadget-body")
            bills.append(driver.find_element(*po).text)
        except Exception as e:
            bills.append(f'{App.exception_message(e)}')
        finally:
            self.pilot_result.append( [account.get("name","Unknown"), bills] )

        logger.debug(f'  @@pilot_internal: END')


if __name__ == "__main__":
    try:
        from operator import itemgetter
        App = RCardMonthly()
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
        print(f'{App.exception_message(e)}')
        if App.driver is not None:
            App.driver.quit()
