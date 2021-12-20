from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium import webdriver
import os
userdata_dir = r'../profile/'    # path to profile folder
username = r'testuser'        # identifier for current user.
os.makedirs(userdata_dir, exist_ok=True)
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=' + userdata_dir + username)
driver = webdriver.Chrome(r'', options=options)
# driver.get("https://mail.aol.com/webmail-std/ja-jp/suite")
driver.get("https://ecnavi.jp/login/")
