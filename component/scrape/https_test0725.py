import requests
from bs4 import BeautifulSoup

base_url = 'https://ssr2.scrape.center/page/'

headers = {}

def parser_html(url : str,headers : dict):
    res = requests.get(
        url = url,
        headers = headers,
        verify = False
    ).content.decode('utf-8')
    soup = BeautifulSoup(
        res,
        'html.parser'
    )
    return soup

def remove_en(text: str):
    import re
    return re.sub(r'[^\u4e00-\u9fff]', '', text)

def scrape_page(page_num: int):
    url = f"{base_url}{page_num}"
    soup = parser_html(url, headers)
    movies = []

    title = soup.select('h2.m-b-sm')
    scores = soup.select('p.m-b-n-sm')
    locate = soup.select('div.info')
    rate = soup.select('div.el-rate')

    if not title:
        return None

    for i in range(len(title)):
        movie = {
            'title': remove_en(title[i].text.strip()),
            'score': scores[i].text.strip() if i < len(scores) else 'N/A',
            'locate': ' '.join(locate[i].text.strip().split()) if i < len(locate) else 'N/A',
            'rate': rate[i].get('aria-valuenow') if i < len(rate) else 'N/A'
        }
        movies.append(movie)

    return movies

page_num = 1
all_movies = []

while True:
    movies = scrape_page(page_num)
    if movies is None or not movies:
        break
    all_movies.extend(movies)
    page_num += 1

import pandas as pd
# 将数据保存到 Excel 文件
df = pd.DataFrame(all_movies)
df.to_excel('movies.xlsx', index=False, engine='openpyxl')

print("Data has been saved to movies.xlsx")