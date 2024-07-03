from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pynput.keyboard import Listener
import time

chrome_options = Options()
chrome_options.binary_location = r"chrome-win64\chrome.exe"
driver_path = r"chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("http://10.120.105.234:5010/")

def on_press(key):
    try:
        if hasattr(key, 'char'):
            key_listener(key.char)
        else:
            key_listener(key)
    except Exception as e:
        print("An error occurred:", e)

def key_listener(key_code):
    if key_code == 'UP' or key_code == 'x':
        remove_btn = driver.find_element('xpath', '//*[@id="remove-btn"]')
        remove_btn.click()
    elif key_code == 'LEFT' or key_code == 'a':
        prev_btn = driver.find_element('xpath', '//*[@id="prev-btn"]')
        prev_btn.click()
    elif key_code == 'DOWN' or key_code == 's':
        save_btn = driver.find_element('xpath', '//*[@id="save-btn"]')
        save_btn.click()
    elif key_code == 'RIGHT' or key_code == 'd':
        next_btn = driver.find_element('xpath', '//*[@id="next-btn"]')
        next_btn.click()

time.sleep(2)

with Listener(on_press=on_press) as listener:
    listener.join()

driver.quit()
