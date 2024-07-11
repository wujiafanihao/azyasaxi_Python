import pandas as pd

# 读取Excel文件
df = pd.read_excel('result.xlsx')

# 找出A列中重复的值
duplicates = df[df['A'].duplicated(keep=False)]

# 打印要删除的内容和行数
for index, row in duplicates.iterrows():
    print(f"删除行 {index + 2}: {row['A']}")  # Excel行号从2开始

# 删除重复行，保留第一次出现的行
df_cleaned = df.drop_duplicates(subset=['A'], keep='first')

# 将结果保存到新的Excel文件
df_cleaned.to_excel('cleaned_file.xlsx', index=False)

print(f"\n共删除了 {len(duplicates)} 行")
print("清理后的文件已保存为 'cleaned_file.xlsx'")