import pandas as pd
import re

def is_chinese_or_english_mixed(s):
    # 正则表达式：匹配至少一个中文字符，并且只包含中文字符和英文字母
    pattern = re.compile(r'^(?=.*[\u4e00-\u9fa5])[\u4e00-\u9fa5a-zA-Z]+$')
    return bool(pattern.match(s))

def clean_excel(file_name):
    # 读取Excel文件
    df = pd.read_excel(file_name, header=None)

    # 遍历A列，检查每个单元格是否符合要求
    rows_to_keep = []
    for index, row in df.iterrows():
        cell_value = str(row[0])  # 确保A列值为字符串
        if is_chinese_or_english_mixed(cell_value):
            rows_to_keep.append(index)

    # 保留符合要求的行
    df_cleaned = df.loc[rows_to_keep]

    # 直接覆盖保存清理后的Excel文件
    df_cleaned.to_excel(file_name, index=False, header=False)

# 使用示例
file_name = "新建 XLSX 工作表.xlsx"
clean_excel(file_name)
