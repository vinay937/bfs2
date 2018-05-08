# from contextlib import closing
# from selenium.webdriver import PhantomJS # pip install selenium
# from selenium.webdriver.support.ui import WebDriverWait

# # use firefox to get page with javascript generated content
# with closing(PhantomJS()) as browser:
#      browser.get('https://newfeedback.bmsit.ac.in/__/__/--/__/__reports/VISHAKHAY')
#      # wait for the page to load
#      WebDriverWait(browser, timeout=10).until(
#          lambda x: x.find_element_by_class_name('total'))
#      # store it to string variable
#      total = browser.find_element_by_class_name('total')

# print(total.find_element_by_xpath('//*[@id="dvContainer"]/table/tbody[2]/tr[11]/td[7]'))
import requests

import psycopg2

conn = psycopg2.connect(database='feedback', user='postgres', password='feedback321', host='128.199.250.218', port='5431')
cursor = conn.cursor()

cursor.execute("SELECT username FROM general_user A, general_user_user_type B WHERE A.id = B.user_id AND B.usertype_id = 4 ORDER BY username;")
data = cursor.fetchall()

for i in data:
	r = requests.get('https://feedback360.bmsit.ac.in/__/__/--/__/__sreports/%s/' %(i[0]))
	print('https://feedback360.bmsit.ac.in/__/__/--/__/__sreports/%s/' %(i[0]))
