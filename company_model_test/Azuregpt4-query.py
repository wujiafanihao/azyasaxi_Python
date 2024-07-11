import pandas as pd
from dotenv import load_dotenv
import os
import time
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate

# 加载环境变量
load_dotenv()

# Azure OpenAI API设置
llm = AzureChatOpenAI(temperature=0.7, azure_deployment='tcl-gpt4o1')

# 模板
template = """
按照我的要求泛化测试集：
1.我会提供原始query给你,你需要参考我例子中的泛化类型,对其进行泛化,泛化的时候不要改变原来query的本意.
2.输出的时候不要markdown格式.
3.泛化的时候尽量贴近人类说话的方式.
4.每句之间无须多出空行,一行一句即可

以下是举例：格式为 原始query-->泛化的query-->泛化的类型依据
例如：
用户:打开爱奇艺
你的回复:打开爱奇艺-->快给我开了爱奇艺-->动词同义

用户:播放云视听快tv
你的回复:播放云视听快tv-->播放云视听快tv啊-->语气词

用户:打开打开云视听
你的回复:打开打开云视听-->云视听打开打开-->语句乱序

用户:播放西瓜视
你的回复:播放西瓜视频-->西瓜视播放一下-->动词同义

用户:打开云打开云视听小电视
你的回复:打开云打开云视听小电视-->打开云打开云视听电视-->实体多字/少字

用户:我想看电视家
你的回复:我想看电视家-->我想看电视家咯-->语气词

用户:换一个呀
你的回复:换一个呀-->换一个吧给我-->语气词

用户:给我看快手tv
你的回复:给我看快手tv-->那啥给我看看快手tv-->动词同义+语气词

用户:打开手机快手
你的回复:打开手机快手-->手机快手开启tv-->动词同义+语句乱序

用户:芒果TV芒果TV
你的回复:芒果TV芒果TV-->芒果芒果TV打开-->实体多字/少字+动词同义

用户:退出对话呀
你的回复:退出对话呀-->快点吧退出对话呀-->意图干扰

用户:播放小快手
你的回复:播放小快手-->播放小快手快手-->实体重复

你的回复格式应为:query-->泛化-->类型(分为动词同义、语气词、语句乱序、实体多字/少字、动词同义+语气词、动词同义+语句乱序、动词同义+实体多字/少字、意图干扰、实体重复等)

用户:{query}
你的回复:

"""

prompt = PromptTemplate(input_variables=["query"], template=template)

def load_queries(file_path):
    """加载query.xlsx文件中的A列数据，不读取标题行"""
    df = pd.read_excel(file_path, usecols=[0], header=None)
    print("Loaded queries:")
    print(df.head())  # 打印前几行以确保从A1列开始加载数据
    return df

def save_to_excel(dataframe, file_path):
    """将数据保存到result.xlsx文件中，追加到A列末尾"""
    last_row = 0
    try:
        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as xls:
                existing_df = pd.read_excel(xls, header=None)
            last_row = existing_df.index[-1] + 1 if not existing_df.empty else 0
            
            with pd.ExcelWriter(file_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                dataframe.to_excel(writer, startrow=last_row, index=False, header=False)
        else:
            dataframe.to_excel(file_path, index=False, header=False)
        
        print(f"Saved {len(dataframe)} new rows to {file_path}, starting from row {last_row + 1}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        # 可以在这里添加备用保存方法，比如保存为CSV
        csv_file = file_path.rsplit('.', 1)[0] + '.csv'
        dataframe.to_csv(csv_file, mode='a', index=False, header=False)
        print(f"Saved data to {csv_file} as a fallback")

def process_queries(df, llm, prompt, result_file):
    """处理查询并调用API"""
    for i in range(0, len(df), 25):
        batch_df = df.iloc[i:i+25]
        queries = "\n".join(batch_df.iloc[:, 0].astype(str).tolist())
        
        query = f"以下是你需要泛化的原始query:\n{queries}"
        formatted_prompt = prompt.format(query=query)
        
        print(f"Processing batch {i // 25 + 1}:")
        # print(formatted_prompt)
        
        while True:
            try:
                response = llm.invoke(formatted_prompt).content
                break
            except Exception as e:
                print(f"Error during API call: {e}")
                print("Retrying in 10 seconds...")
                time.sleep(10)
        
        print("API response:\n" + response + '\n')
        
        response_lines = response.split("\n")
        result_df = pd.DataFrame(columns=['query'])
        for line in response_lines:
            if line.strip():
                result_df = result_df._append({'query': line.strip()}, ignore_index=True)
        
        save_to_excel(result_df, result_file)

def main():
    input_file = 'query.xlsx'
    output_file = 'result.xlsx'
    
    queries_df = load_queries(input_file)
    process_queries(queries_df, llm, prompt, output_file)
    
    print("所有查询已处理并保存到result.xlsx文件中。")

if __name__ == "__main__":
    main()
