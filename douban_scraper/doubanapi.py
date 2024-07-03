from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os
import openpyxl
import time

output_file = "douban.xlsx"

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

current_row = ws.max_row + 1

def save_title_to_excel(cleaned_title,actor_info):
    global current_row
    combined_info = f"{cleaned_title} --> {actor_info}"
    ws.append([combined_info])
    wb.save(output_file)
    current_row += 1

def clean_title(title):
    cleaned_title = re.sub(r'[^\w\s]', '', title)
    cleaned_title = cleaned_title.replace(" ", "")
    return cleaned_title

def get_actor_info(film_info):
    try:
        parts = film_info.split(" / ")
        actors = parts[-1].split()
        actor = actors[0].split(" ")
        first_actor = actor[0]
        return first_actor
    except Exception as e:
        print(f"Error extracting actor info: {e}")
        return "Unknown"

# def get_actor_info(film_info):
#     try:
#         # 将 '/' 替换为 '\t'
#         updated_info = film_info.replace("/", "-->")
#         return updated_info
#     except Exception as e:
#         print(f"Error extracting actor info: {e}")
#         return "Unknown"
        
def get_movie_details(driver, wait, index):
    # 动态选择影片的CSS选择器
    movie_selector = f"#app > div > div.explore-main > ul > li:nth-child({index})"
    
    # 等待指定影片元素加载完成
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, movie_selector)))
    
    # 获取页面内容
    page_source = driver.page_source
    
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # 定位目标元素
    title_span = soup.select_one(f"{movie_selector} > a > div > div.drc-subject-card-main > div > div.drc-subject-info-title > span")
    title_div = soup.select_one(f"{movie_selector} > a > div > div.drc-subject-card-main > div > div.drc-subject-info-title > div")
    
    # 获取影片信息
    title_span_text = title_span.text if title_span else "N/A"
    film_info = title_div.text if title_div else "N/A"

    cleaned_title = clean_title(title_span_text)
    actor_info = get_actor_info(film_info)

    print(f"movie:{title_span_text},info:{film_info}")  
    
    return cleaned_title, actor_info

def scroll_down(driver, wait):
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # Wait for a while to let the page load

    # Check if there is a "Load More" button
    load_more_button = driver.find_elements(By.CSS_SELECTOR, "#app > div > div.explore-main > div > button")
    if load_more_button:
        load_more_button[0].click()  # Click the "Load More" button
        time.sleep(1)  # Wait for a while to let the page load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#app > div > div.explore-main > ul > li:last-child")))  # Wait for the last movie element to load

def main():
    # 设置WebDriver（这里以Chrome为例）
    chrome_options = Options()
    chrome_options.binary_location = r"F:\桌面\python\chrome-win64\chrome.exe"
    driver_path = r"F:\桌面\python\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 打开目标网址
        driver.get('https://movie.douban.com/tv/')
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 等待按下s键开始获取影片信息
        print("按下 's' 键以开始获取影片信息...")
        while True:
            if keyboard.is_pressed('s'):
                break
            time.sleep(0.1)

        # 循环获取多个影片信息
        index = 1
        while True:
            try:
                cleaned_title, actor_info = get_movie_details(driver, wait, index)
                print(f"Movie {index}:")
                print(f"Saved {cleaned_title} --> {actor_info}")
                save_title_to_excel(cleaned_title, actor_info)
                index += 1
                time.sleep(1)  # 等待一段时间以确保页面加载完成
                scroll_down(driver, wait)
            except Exception as e:  
                print(f"No more movies found or error occurred: {e}")
                break
    finally:
        # 关闭WebDriver
        driver.quit()

if __name__ == "__main__":
    import keyboard  # 引入keyboard库以监听键盘事件
    main()
