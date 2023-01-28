from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from RPAbase.InfoseekBase import RakutenBase
from time import sleep

class MaildepointBase(RakutenBase):
    """
    Login/Logout utility for MailDePoint.
    -- Use InfoseekBase, then Nothing else is needed.
    """
