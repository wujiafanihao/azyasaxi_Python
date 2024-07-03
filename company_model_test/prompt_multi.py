from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.base import LLMChain
from langchain_core.prompts import PromptTemplate

api_url = "http://localhost:8000/v1"
api_key = "Bearer sk-ab273b67e6e64f399870cf37b33cf34f"

import openpyxl
import os

output_file = "douban_answer_copy.xlsx"

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

current_row = ws.max_row + 1

def chat_response(query):

    template = """
    现在有一个电视他接了智能助手，而你作为用户在测试他的性能，现在你需要想实体语料。
    对于以下例子，帮我按照否定词规则，泛化出新的实体.
        输出请按照以下格式：泛化类型-->泛化-->实体
        例如：
        否定词-->不是国产的电影搜一下
        否定词-->最新的电影不要爱情片
        否定词-->帮我找个电视剧不要古装的
        否定词-->不要播歌了
        否定词-->找动漫不要古装的
        否定词-->屏幕别搞这么暗
        注意：只允许讨论电视和音乐相关的，且每次生成不得与之前重复

    我需要{question}的
    
    {chat_history}
    Human: {question}
    Chatbot:"""
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"], 
        template=template
    )
    memory = ConversationBufferWindowMemory(memory_key="chat_history",return_messages=True,k=6)

    llm_chain = LLMChain(
        llm = ChatOpenAI(model="gpt-3.5-turbo", base_url=api_url, api_key=api_key),
        prompt=prompt, 
        verbose=True, 
        memory=memory,
    )
 
    # 调用 invoke 方法并传递 headers
    response = llm_chain.invoke(input=query)
    content = response['text']
    memory.buffer
    return content

def save_to_excel(result, current_row):
    for line in result.split('\n'):
        ws.cell(row=current_row, column=1, value=line)
        current_row += 1
    current_row += 1  
    wb.save(output_file)
    return current_row

if __name__ == "__main__":
    while True:
        query = "请开始生成"
        result = chat_response(query)
        print(result)
        current_row = save_to_excel(result, current_row)