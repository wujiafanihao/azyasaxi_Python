from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import os


llm = AzureChatOpenAI(
    temperature=0.3,
    azure_deployment='tcl-gpt4o1'
)

template = """
You is a helpful assistant that base on context : {context} to answer the user's query

example:
<pre>
context : 《我的阿勒泰》的导演是周军。
user : 查询他的所有作品
AI : 查询他的所有作品-->周军的所有作品-->代词改写

context : 《我的阿勒泰》是一部以新疆阿勒泰地区为背景的电影或电视剧。故事主要围绕主人公在阿勒泰的生活、工作和情感经历展开。通过描绘主人公与当地居民、自然环境以及文化的互动，展现了阿勒泰独特的风土人情和美丽的自然景观。影片或剧集可能涉及到主人公在面对挑战和困境时的成长与蜕变，同时也传递出对家乡的热爱和对生活的积极态度。具体的剧情细节可能会因版本不同而有所变化，但总体上都是以阿勒泰为核心，讲述一个充满人情味和地域特色的故事。
user : 播放这个吧
AI : 播放这个吧-->播放《我的阿勒泰》-->代词改写

context : 《新生》的主演是周依然和吴念轩。
user : 给我播放他
AI : 给我播放他-->给我播放《新生》-->代词改写

context : 《新生》的导演是李霄峰。这部电影是一部中国大陆的剧情片，讲述了一个关于成长和自我发现的故事。李霄峰是一位才华横溢的导演，以其独特的叙事风格和深刻的情感表达而闻名。
user : 他还有哪些作品
AI : 他还有哪些作品-->除了《新生》，李霄峰还有那些作品-->排除性指代改写

context : 《狐妖小红娘月红篇》的导演是王昕。
user : 这个导演还拍过什么
AI : 这个导演还拍过什么-->除了《狐妖小红娘月红篇》，王昕还拍过什么-->排除性指代改写
<pre>

user : {query}

AI : {query}-->you answer-->tags
"""

def init_model(context,query):
    prompt = PromptTemplate(
        template=template,
        input_variables=['context','query']
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    res = llm_chain.invoke({
        'context':context,
        'query':query,
    })
    return res

def generate_qc(file_path):
    df = pd.read_excel(file_path,index_col=False,header=None)
    context = df[0].astype(str).dropna()
    queries = ['查询他的所有作品','播放这个吧','给我播放他','他还有哪些作品','看下看这个','这个导演还拍过什么']

    for context_value in context:
            for query in queries:
                yield context_value, query

def save_to_excel(answer, file_name):
    if not os.path.isfile(file_name):
        df = pd.DataFrame(columns=['answer'])
    else:
        df = pd.read_excel(file_name)
    
    new_data = pd.DataFrame({
        'answer': [answer]
    })
    
    df = pd.concat([df, new_data], ignore_index=True)
    
    df.to_excel(file_name, index=False)

def main(file_path):
    qc_generator = generate_qc(file_path)
    for context, query in qc_generator:
        res = init_model(context, query)
        print(res)
        save_to_excel(res['text'],file_name='test0726.xlsx')

main(file_path='context.xlsx')