from contextlib import closing
from selenium.webdriver import PhantomJS # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait

# use firefox to get page with javascript generated content
with closing(PhantomJS()) as browser:
     browser.get('https://newfeedback.bmsit.ac.in/__/__/--/__/__reports/VISHAKHAY')
     # wait for the page to load
     WebDriverWait(browser, timeout=10).until(
         lambda x: x.find_element_by_class_name('total'))
     # store it to string variable
     total = browser.find_element_by_class_name('total')

print(total.find_element_by_xpath('//*[@id="dvContainer"]/table/tbody[2]/tr[11]/td[7]'))
