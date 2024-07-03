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
    请根据以下指示生成知识问答内容，并确保内容的真实性和创造性。输出格式如下：
            外部服务内容是：提供一些背景信息或上下文(可以带符号)-->用户的问题(注意不要带任何符号，包括书名号)-->将用户的问题或请求转化为更明确的指令(注意不要带任何符号，包括书名号)。

            示例：
            外部服务内容是：《惜花芷》的女主是花芷。你喜欢看古言小说吗？我也很喜欢呢-->是谁演的-->《惜花芷》的女主是花芷是谁演的
            外部服务内容是：我不太清楚“背着善宰跑”是什么剧情的电视剧呢，我平时喜欢看一些青春校园剧，你有兴趣吗？-->直接搜这个-->直接搜背着善宰跑
            外部服务内容是：《甄嬛传》是一部宫斗类型的电视剧。-->播这个的主题曲-->播放甄嬛传的主题曲
            外部服务内容是：《甄嬛传》是一部宫斗类型的电视剧。-->播这个的片尾曲-->播放甄嬛传的片尾曲

            请注意：
            1. 你可以发挥想象去问一些百科类的问题，不需要完全跟着实体片名走。
            2. 确保生成的内容具有真实性，可以根据实际情况提供准确的信息。

            例如：
            外部服务内容是：主角是伊森·亨特，由汤姆·克鲁斯饰演。-->他还演过什么-->汤姆·克鲁斯还演过什么
            外部服务内容是：这句台词来自于电影《楼外楼》。-->看这个快播放-->楼外楼
            外部服务内容是：这句台词出自电视剧《回家的诱惑》。-->就看这个快点播-->回家的诱惑
            外部服务内容是：“元芳你怎么看”出自电视剧《神探狄仁杰》。-->找这个的片源-->神探狄仁杰
            外部服务内容是：“我问你这瓜保熟吗”出自电视剧《征服》。-->就看这个电视剧-->征服
            外部服务内容是：陈妍希的老公是陈晓。你想了解一下他们的爱情故事吗？-->了解一下-->了解一下陈妍希和陈晓的爱情故事
            外部服务内容是：陈晓是一位男性演员，他的妻子是陈妍希。我平时喜欢绘画、唱歌，你呢？-->看她老婆的电视剧-->看陈妍希的电视剧


            我需要你生成十组,三组为实体片名，三组为演员，后面四组请靠你自己的发挥想一些问答的题目，包括百科，音乐，新闻等等的领域问答。
            用户的问题和将用户的问题或请求转化为更明确的指令这两步不要带有标点符号
            每组一个换行隔开，生成的内容应符合上述格式和要求。
            确保每轮生成的和上一轮不要重复且不要一直消费一部影片，音乐等

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
    query_list = ['科学类', '新闻类', '教育类', '体育类', '音乐类', '人工智能领域类']
    query_index = 0
    while True:
        query = query_list[query_index]
        print(query)
        result = chat_response(query)
        print(result)
        current_row = save_to_excel(result, current_row)
        query_index = (query_index + 1) % len(query_list)