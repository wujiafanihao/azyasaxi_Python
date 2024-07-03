import pandas as pd

# 定义文件路径
file_path = 'Actor.xlsx'

def read_actor_info(file_path):
    """
    读取Excel文件并返回DataFrame
    :param file_path: Excel文件的路径
    :return: 包含Excel数据的DataFrame
    """
    # 读取Excel文件
    df = pd.read_excel(file_path, header=None)
    return df

def get_actor_info(df, index):
    """
    获取指定索引行的演员名和代表作
    :param df: 包含Excel数据的DataFrame
    :param index: 当前行索引
    :return: 演员名和代表作列表
    """
    # 获取指定索引行的数据
    row = df.iloc[index]
    # 获取演员名
    actor_name = row[0]
    # 获取代表作，并过滤掉NaN值
    works = row[1:].dropna().tolist()
    return actor_name, works

if __name__ == "__main__":
    # 读取Excel文件并获取DataFrame
    df = read_actor_info(file_path)
    # 初始化行索引
    index = 0

    # 使用while True循环逐行读取数据
    while True:
        # 获取当前行的演员名和代表作
        actor_name, works = get_actor_info(df, index)
        
        # 如果演员名为空，停止读取
        if pd.isna(actor_name):
            break
        
        # 打印演员名
        print(f"演员: {actor_name}")
        # 打印代表作
        print("代表作:", end=" ")
        for work in works:
            print(work, end=", " if work != works[-1] else "\n")
        
        # 增加行索引，读取下一行
        index += 1