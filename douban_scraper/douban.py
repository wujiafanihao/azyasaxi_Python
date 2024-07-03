from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import openpyxl
import keyboard

output_file = "douban_video_id.xlsx"

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

movie_id = []
movie_name = []
current_row = ws.max_row + 1
last_added_time = 0  # 记录最后一次添加元素的时间
first_load_more_button_missing = False  # 标志变量，用于控制消息的显示

def scroll_down(driver, wait):
    global first_load_more_button_missing
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    load_more_button = driver.find_elements(By.CSS_SELECTOR, "#app > div > div.explore-main > div > button")
    if not load_more_button:
        if not first_load_more_button_missing:
            print("没有找到加载更多按钮，可能已经加载完毕或页面结构发生变化。")
            first_load_more_button_missing = True
        return
    load_more_button[0].click()  
    time.sleep(1)  
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div > div.explore-main > ul > li:last-child")))  

def get_movie_ids(driver, wait, target_div):
    global movie_id, last_added_time
    # 获取target_div下的所有a标签
    links = target_div.find_elements(By.TAG_NAME, 'a')
    scroll_down(driver, wait)
    for link in links:
        href = link.get_attribute('href')
        # 提取href中的数字部分
        if href:
            # 使用正则表达式提取数字
            import re
            match = re.search(r'/tv/(\d+)', href)
            if match:
                number = match.group(1)
                # 检查数字是否已存在于数组中
                if number not in movie_id:
                    movie_id.append(number)
                    last_added_time = time.time()  
                    print(f"新数字添加到数组：{number}")
                    print(f"当前数组长度：{len(movie_id)}")
                    print(f"当前数组内容：{movie_id}")
                    print("---")

    if time.time() - last_added_time > 7 and not driver.find_elements(By.CSS_SELECTOR, "#app > div > div.explore-main > div > button"):
        print("超过5秒没有添加新元素，退出监控。")
        save_title_to_excel()  
        driver.quit()

def save_title_to_excel():
    global current_row
    for number in movie_id:
        combined_info = f"{number}"
        ws.append([combined_info])
        current_row += 1
    wb.save(output_file)

def main():
    chrome_options = Options()
    chrome_options.binary_location = r"F:\桌面\python\chrome-win64\chrome.exe"
    driver_path = r"F:\桌面\python\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://movie.douban.com/tv/"
    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        print("按下 's' 键以开始获取影片信息...")
        while True:
            if keyboard.is_pressed('s'):
                break
            time.sleep(0.1)

        target_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#app > div > div.explore-main')))
        while True:
            try:
                get_movie_ids(driver, wait, target_div)
                time.sleep(2)
            except Exception as e:  
                print(f"No more movies found or error occurred: {e}")
                break
    finally:
        driver.quit()    

if __name__ == "__main__":
    main()