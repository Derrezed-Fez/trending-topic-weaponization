from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui

options = Options()
#For some reason both of these paths have to be absolute, so these will need to be changed before running
options.binary_location = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

browser = webdriver.Firefox(executable_path='C:\\Users\\Zane\\trending-topic-weaponization\\geckodriver.exe', options = options)

browser.get('http://www.bing.com')
assert 'Bing' in browser.title

data = json.load(open('virus_total_results_formatted.json', encoding='utf-8'))
metadata = dict()
for key, value in data.items():
    for key_1, value_1 in value.items():
        if key_1 == 'results':
            for key_2, value_2 in value_1.items():
                if value_2 != 'URL Does Not Exist' and (value_2['malicious'] != 0 or value_2['suspicious'] != 0):
                    try:
                        keyword = key_2.replace('.us', '').replace('.co', '').replace('.net', '').replace('.com', '').replace('.io', '').replace('.org', '')
                        full_url = 'http://www.' + key_2.lower()
                        browser.get(full_url)
                        metadata[key_2] = dict()
                        metadata[key_2]['in_url'] = True
                        metadata[key_2]['in_page_source'] = keyword.lower() in browser.page_source
                        try:
                            elem = browser.find_element(By.XPATH,"//meta[@name='description']")
                            metadata[key_2]['in_metadata_description'] = keyword.lower() in elem.get_attribute('innerHTML')
                        except Exception:
                            print('No metadata description for ' + key_2)
                            metadata[key_2]['in_metadata_description'] = False

                        elems = browser.find_elements(By.XPATH, "//a[@href]")
                        outgoing_links, internal_links = list(), list()
                        for elem in elems:
                            link = elem.get_attribute("href")
                            if full_url in link:
                                internal_links.append(link)
                            else:
                                outgoing_links.append(link)
                        if len(outgoing_links) > 0:
                            metadata[key_2]['in_outgoing_links'] = True
                        else:
                            metadata[key_2]['in_outgoing_links'] = False
                        metadata[key_2]['internal_links'] = internal_links
                        metadata[key_2]['outgoing_links'] = outgoing_links
                        time.sleep(0.5)
                    except Exception:
                        print('DNS Could Not be Resolved for ' + key_2)

with open('keywords_metadata.json', 'w') as fp:
    json.dump(metadata, fp)

browser.quit()