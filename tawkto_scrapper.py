import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

url = "https://dashboard.tawk.to/#/messaging"

#set up browser ao
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(chrome_options=chrome_options)
# browser = webdriver.Chrome()
browser.set_page_load_timeout(15)
wait = WebDriverWait(browser, 500)


browser.get(url)

#login
username = browser.find_element_by_id("email")
password = browser.find_element_by_id("password")
username.send_keys("xander.analytics@gmail.com")
password.send_keys("xander2017")

login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
login_attempt.submit()

time.sleep(5)

browser.get(url)

time.sleep(15)


#test cac cach de load message
# wait.until(EC.visibility_of_element_located((By.ID,'5951ef5450fd5105d0c82d59')))
# vicare_tab_select = browser.find_element_by_id("5951ef5450fd5105d0c82d59").click()
# xander_tab_select = browser.find_element_by_id("582d5d478147e4684e46f1b9").click()
# wait.until(EC.visibility_of_element_located((By.ID, 'conversation-list')))
main_messaging = browser.find_element_by_class_name("view-section")
print(main_messaging)
# main_messaging.send_keys(Keys.END)
time.sleep(10)

soup = BeautifulSoup(browser.page_source, "html.parser")

# print soup.prettify()

time.sleep(5)

#lay id cac row message
div_tag = soup.find("div", {"id": "conversation-list"})
# print div_tag.prettify()
# print "\n\n"
table = div_tag.find("table")
# # print table.prettify()
# # print "\n\n"
row = table.find_all("tr")
num_of_rows = 0
print "these are the rows"
for tr in row:
    num_of_rows += 1
    print tr.prettify()
print num_of_rows
