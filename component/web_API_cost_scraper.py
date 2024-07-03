import requests
from bs4 import BeautifulSoup
import pandas as pd

# 目标 URL
url = "https://aigcrank.cn/llmprice/"

# 发送 HTTP 请求
response = requests.get(url)
response.raise_for_status()  # 检查请求是否成功

# 解析 HTML 内容
soup = BeautifulSoup(response.content, 'html.parser')

# 找到数据表格
table = soup.find('table', {'id': 'tablepress-llm'})

# 提取表头
header = [th.text for th in table.find('thead').find_all('th')]

# 提取数据行
data = []
rows = table.find('tbody').find_all('tr')
for row in rows:
    cells = row.find_all('td')
    data.append([cell.text for cell in cells])

# 创建 DataFrame
df = pd.DataFrame(data, columns=header)

# 去掉不需要的列
columns_to_drop = ["产品链接", "价格链接"]
df.drop(columns=columns_to_drop, inplace=True)

# 打印数据
print(df)

# 保存数据到 CSV 文件
df.to_csv("llmprice_data.csv", index=False, encoding="utf-8")
