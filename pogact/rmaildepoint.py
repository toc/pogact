# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class rcard(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)

        driver.get("https://member.pointmail.rakuten.co.jp/box")
        driver.find_element_by_id("loginInner_u").clear()
        driver.find_element_by_id("loginInner_u").send_keys("id")
        driver.find_element_by_id("loginInner_p").clear()
        driver.find_element_by_id("loginInner_p").send_keys("pw")
        wait.until(EC.visibility_of_element_located((By.NAME, "submit"))).click()

        wh_base = driver.current_window_handle

        driver.find_element_by_link_text(u"メールボックス").click()

        # while True:
        try:
            driver.find_element_by_link_text(u"未獲得").click()
            print(f'  wait for visibility_of_element_located: CLASS_NAME:mailboxBox')
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"mailboxBox")))

            mailbox = driver.find_element_by_class_name("mailboxBox")
            mails = mailbox.find_elements_by_xpath("ul/li")
            print(len(mails))
            point_contents = []

            for mail in mails:
                class_value = mail.get_attribute("class")
                print(class_value)
                if class_value != "teamSiteSubject":
                    # ポイント獲得可能メール発見
                    break
            if class_value == "teamSiteSubject":
                # 広告メール以外は存在せず。
                pass
            else:
                # ポイント獲得可能メール発見
                divs = mail.find_elements_by_xpath("div")
                alt_text = divs[0].find_element_by_xpath("img").get_attribute("alt")
                content = divs[1].find_element_by_xpath("a/p").text
                # point_contents.append([alt_text, content])
                print(f"  {alt_text} {content}")
                divs[1].find_element_by_xpath("a").click()
                while True:
                    pager = driver.find_elements_by_class_name("pager")
                    print(driver.find_element_by_xpath(r'//*[@id="mailContents"]/div[2]/div[1]/div[2]/p'))
                    point_urls = driver.find_elements_by_class_name("point_url")
                    point_urls_num = len(point_urls)
                    if point_urls_num > 0:
                        point_url = point_urls[0].find_element_by_xpath("a")
                        print(f'  {point_urls_num} {point_url.get_attribute("href")}')
                        point_url.click()
                        print(f'  -- click')
                        time.sleep(0.5)
                        driver.switch_to.window(driver.window_handles[1])
                        print(f'  -- switch to new page, and wait presence of all elements')
                        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
                        # a = driver.find_elements_by_tag_name(r'a')
                        # WebDriverWait(driver, 15).until(EC.visibility_of(a[-1]))
                        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.TAG_NAME, r'body')))
                        print(f'  -- close new page')
                        driver.close()
                        print(f'  -- switch to old page')
                        driver.switch_to.window(driver.window_handles[0])
                    else:
                        print(f'  No point_url found.')
                    pager_next = pager[0].find_elements_by_xpath(r'ul/li[2]/a')
                    if len(pager_next) > 0:
                        pager_next[0].click()
                        # wait.until...
                    else:
                        break
        except Exception as e:
            print(e.args)
            # driver.back()
            
            print(point_contents)


    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
