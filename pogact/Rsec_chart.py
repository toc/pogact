# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class UntitledTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path=r'')
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_untitled_test_case(self):
        driver = self.driver
        driver.get("https://www.google.com/search?q=%E6%A5%BD%E5%A4%A9%E8%A8%BC%E5%88%B8&rlz=1C1GCEB_enJP1058JP1058&oq=%E6%A5%BD%E5%A4%A9%E8%A8%BC%E5%88%B8&gs_lcrp=EgZjaHJvbWUqDggAEEUYJxg7GIAEGIoFMg4IABBFGCcYOxiABBiKBTIKCAEQABgDGAQYJTIQCAIQABiDARixAxiABBiKBTIQCAMQABiDARixAxiABBiKBTIGCAQQRRg9MgYIBRBFGD0yBggGEEUYQTIGCAcQRRg90gEIMjY0N2owajSoAgCwAgA&sourceid=chrome&ie=UTF-8")
        driver.get("https://finance.yahoo.co.jp/portfolio/detail?portfolioId=26&isUpdate=1700305265335")
        driver.get("https://www.google.com/search?q=%E6%A5%BD%E5%A4%A9%E8%A8%BC%E5%88%B8&rlz=1C1GCEB_enJP1058JP1058&oq=%E6%A5%BD%E5%A4%A9%E8%A8%BC%E5%88%B8&gs_lcrp=EgZjaHJvbWUqDggAEEUYJxg7GIAEGIoFMg4IABBFGCcYOxiABBiKBTIKCAEQABgDGAQYJTIQCAIQABiDARixAxiABBiKBTIQCAMQABiDARixAxiABBiKBTIGCAQQRRg9MgYIBRBFGD0yBggGEEUYQTIGCAcQRRg90gEIMjY0N2owajSoAgCwAgA&sourceid=chrome&ie=UTF-8")
        driver.find_element_by_link_text(u"ログイン").click()
        driver.get("https://www.rakuten-sec.co.jp/ITS/V_ACT_Login.html")
        driver.find_element_by_id("form-login-id").clear()
        driver.find_element_by_id("form-login-id").send_keys("AVXG5897")
        driver.find_element_by_id("form-login-pass").clear()
        driver.find_element_by_id("form-login-pass").send_keys("sR5833m397")
        driver.find_element_by_id("login-btn").click()
        driver.get("https://member.rakuten-sec.co.jp/app/Login.do")
        driver.get("https://member.rakuten-sec.co.jp/app/com_page_template.do;BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f?type=home_compulsion_list&BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f")
        driver.find_element_by_id("search-stock-01").click()
        driver.find_element_by_id("search-stock-01").clear()
        driver.find_element_by_id("search-stock-01").send_keys("8848")
        driver.find_element_by_id("search-stock-01").send_keys(Keys.ENTER)
        driver.get("https://member.rakuten-sec.co.jp/app/info_jp_prc_search.do;BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f?eventType=search")
        driver.find_element_by_link_text(u"大きなチャートを見る").click()
        driver.get("https://member.rakuten-sec.co.jp/app/info_jp_prc_stock.do;BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f?eventType=init&infoInit=1&contentId=3&type=&sub_type=&local=&dscrCd=8848&marketCd=1&gmn=J&smn=01&lmn=01&fmn=01")
        driver.find_element_by_xpath("//input[@type='image']").click()
        #ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
        driver.get("https://member.rakuten-sec.co.jp/app/info_jp_prc_stock.do;BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f?marketCdForCmb=1&x=92&y=19&dscrCd=88480&marketCd=1&contentId=3&eventType=search&type=&sub_type=&local=&searchType=&chartType=&chartPeriod=1&underDispType=&dscrCdNm=&industryCd=")
        driver.get("https://hs.trkd-asia.com/rakutenseccht/chart.jsp?ric=8848.T&style=2&int=11&token=2B18BE097ACD26C9FF5CF9A4FE25777DAD53D4E80C8A35230FACB77688FE1F15C4B57A8B9C8FE51565A6DD71BFB0A8CA051E6BBBA9ACD5BD9EEE0590")
        driver.get("https://hs.trkd-asia.com/rakutenseccht/ui/rc5?lang=ja&ric=8848.T&style=2&int=11&token=2B18BE097ACD26C9FF5CF9A4FE25777DAD53D4E80C8A35230FACB77688FE1F15C4B57A8B9C8FE51565A6DD71BFB0A8CA051E6BBBA9ACD5BD9EEE0590")
        driver.get("https://member.rakuten-sec.co.jp/app/info_jp_prc_stock.do;BV_SessionID=97B0E29AC200053150E5AF27D0952A89.ee24ea7f?marketCdForCmb=1&x=92&y=19&dscrCd=88480&marketCd=1&contentId=3&eventType=search&type=&sub_type=&local=&searchType=&chartType=&chartPeriod=1&underDispType=&dscrCdNm=&industryCd=")
        driver.get("https://finance.yahoo.co.jp/portfolio/detail?portfolioId=26&isUpdate=1700305265335")
        driver.get("https://hs.trkd-asia.com/rakutenseccht/ui/rc5?lang=ja&ric=8848.T&style=2&int=11&token=2B18BE097ACD26C9FF5CF9A4FE25777DAD53D4E80C8A35230FACB77688FE1F15C4B57A8B9C8FE51565A6DD71BFB0A8CA051E6BBBA9ACD5BD9EEE0590")
        driver.find_element_by_id("mi-period").click()
        driver.find_element_by_xpath("//div[@id='mi-period']/div/div[8]").click()
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='今年'])[3]/following::span[6]").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div/div[2]").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div[2]/div/canvas").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div[2]/div/canvas").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div/div/div").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div/div/div/div[2]/div[2]/div/div[2]/select").click()
        Select(driver.find_element_by_xpath("//div[@id='c5widget']/div/div/div/div[2]/div[2]/div/div[2]/select")).select_by_visible_text("NYSE")
        driver.find_element_by_xpath("//div[@name='EQTY']").click()
        driver.find_element_by_xpath("//input[@value='']").clear()
        driver.find_element_by_xpath("//input[@value='']").send_keys("HDV")
        driver.find_element_by_xpath("//input[@value='']").send_keys(Keys.ENTER)
        driver.get("https://finance.yahoo.co.jp/portfolio/detail?portfolioId=26&isUpdate=1700305265335")
        driver.get("https://hs.trkd-asia.com/rakutenseccht/ui/rc5?lang=ja&ric=8848.T&style=2&int=11&token=2B18BE097ACD26C9FF5CF9A4FE25777DAD53D4E80C8A35230FACB77688FE1F15C4B57A8B9C8FE51565A6DD71BFB0A8CA051E6BBBA9ACD5BD9EEE0590")
        driver.find_element_by_id("c5widget").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div[2]/div/canvas").click()
        driver.find_element_by_id("mi-period").click()
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='iシェアーズ　コア米国高配当株 ETF'])[1]/following::span[5]").click()
        driver.find_element_by_xpath(u"(.//*[normalize-space(text()) and normalize-space(.)='今月'])[1]/following::span[4]").click()
        driver.find_element_by_xpath("//div[@id='c5widget']/div/div[2]").click()
    
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
