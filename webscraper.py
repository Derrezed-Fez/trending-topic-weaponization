from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

options = Options()
options.binary_location = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

browser = webdriver.Firefox(executable_path='C:\\Users\\OWNERS-PC\\Documents\\Workspace2\\geckodriver.exe', options = options)

browser.get('http://www.bing.com')
assert 'Bing' in browser.title

search_bar = browser.find_element_by_id("sb_form_q")
search_bar.send_keys('youtube' + Keys.RETURN)

browser.quit()