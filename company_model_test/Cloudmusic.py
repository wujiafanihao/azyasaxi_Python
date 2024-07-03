from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_movie_ids(driver):
    table = driver.find_element(By.TAG_NAME, "table")

    a_tags = table.find_elements(By.TAG_NAME, "a")

    # 提取并打印所有 a 标签的 href 属性，仅包含 "song?id="，并去重
    hrefs = {a.get_attribute("href") for a in a_tags if "song?id=" in a.get_attribute("href")}
    for href in hrefs:
        import re
        match = re.search(r'song\?id=(\d+)',href)
        return match.group(1)

def main():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    driver_path = r"F:\桌面\python\chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://music.163.com/#/discover/toplist?id=19723756")
        
        driver.switch_to.frame("contentFrame")
        
        music_id = get_movie_ids(driver)
        print(music_id)

        if music_id:
            driver.get(f'https://music.163.com/#/song?id={music_id}')
            driver.switch_to.frame("contentFrame")
            em_element = driver.find_element(By.XPATH, "//*[@id='auto-id-p1EqPvM23xe4ikgK']/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/div/em")
            print(em_element)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()