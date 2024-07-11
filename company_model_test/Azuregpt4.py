from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.base import ConversationChain
import pandas as pd

conversation = None

propose_prompt = """
现在我需要你生成的分类分别是：
1.句式泛化：就是大众化的词，以及一些模糊的指令
2.意图干扰：干扰想要表达的话

句式泛化的实例:
句式泛化-->播放云视听-->AppControl-->打开云视听小电视
句式泛化-->华小华数鲜时光-->AppControl-->打开华数鲜时光
句式泛化-->哔哩哔哩-->AppControl-->打开哔哩哔哩
句式泛化-->往下走一个-->command-->往下滑
句式泛化-->音量给我转到15-->command-->音量给我调到15
句式泛化-->搜索龙猫完整版中文-->movie-->搜索中文版的龙猫
句式泛化-->伶可兄-->movie-->伶可兄弟
句式泛化-->播放不要钱的复仇者联盟主题曲-->music-->播放免费的复仇者联盟主题曲
句式泛化-->播放邓紫棋免费倒数歌曲-->music-->播放免费的邓紫棋的倒数

意图干扰的实例:
意图干扰-->让我来说抖音-->AppControl-->打开抖音
意图干扰-->全世界最好的鲜时光-->AppControl-->打开华数鲜时光
意图干扰-->播放网易云我喜欢里面的歌-->AppControl-->打开网易云
意图干扰-->嗯打开我的应用我的应用-->AppControl-->打开我的应用
意图干扰-->叫什么来着对莲花什么楼-->movie-->莲花楼
意图干扰-->看个喜羊羊与灰太狼看个-->movie-->喜羊羊与灰太狼
意图干扰-->叫什么来着请和我这样的恋爱吧-->movie-->请和我这样的恋爱吧
意图干扰-->看个好事成双马上播放-->movie-->好事成双
意图干扰-->我记得叫什么来着斗破什么的-->movie-->斗破苍穹	
意图干扰-->中央一台你别叫-->movie-->中央一台
意图干扰-->屏幕调到了最亮-->command-->100亮度
意图干扰-->音量啊调到那个15大小-->command-->调到15的音量
意图干扰-->屏幕调到最亮好吧-->command-->100亮度
意图干扰-->wifi开关给我打开-->command-->打开wifi
意图干扰-->音量太太大了小一点-->command-->降低音量
意图干扰-->音量小音量太大了小一点-->command-->降低音量
"""

entity_prompt = """
现在我需要你生成的分类分别是：
1.人物关系
2.实体别名:例如复仇者联盟，别名为复联

人物关系的实例：
人物关系-->陈妍希老公的电影-->movie-->陈晓的电影	
人物关系-->蔡少芬的老公的电影-->movie-->张晋的电影
人物关系-->列出邓超老婆的电视剧-->movie-->孙俪的电视剧
人物关系-->播放叶倩文老公的歌-->music-->林子祥的歌
人物关系-->播放付笛声老婆的乐曲-->music-->任静的乐曲
人物关系-->我想听听任静丈夫的音乐-->music-->付笛声的音乐

实体别名的实例:
实体别名-->我要看药神-->movie-->我不是药神
实体别名-->王牌第五季-->movie-->指代王牌对王牌第五季）
实体别名-->播放小黄人-->movie-->神偷奶爸
实体别名-->我想看凌波丽-->movie-->指代EVA
实体别名-->播放坤坤的歌-->music-->蔡徐坤
实体别名-->我应该在车底不应该在车里-->music-->他一定很爱你
实体别名-->听六眼飞鱼-->music-->勇气
实体别名-->播放挖呀挖呀挖-->music-->花园种花

实例只是用作我想表达的意思,不要抄实例
"""

content_prompt = """
现在我需要你生成的分类分别是：
1.组合条件搜索

组合条件搜索的实例是：
组合条件搜索-->玩具总动员2约翰拉塞特的电影-->movie
组合条件搜索-->电影中国大陆2023年银河写手-->movie	
组合条件搜索-->电影2016年中国大陆奇幻-->movie	
组合条件搜索-->阿甘正传罗伯特泽米吉斯的电影-->movie	
组合条件搜索-->喜剧电影2011年中国台湾-->movie
组合条件搜索-->伊万麦克格雷格的2003年家庭片-->movie
组合条件搜索-->老炮儿冯小刚-->movie
组合条件搜索-->上个世纪90年代的老电视剧免费的-->movie	
组合条件搜索-->隐藏人物2016年电影美国-->movie	
组合条件搜索-->俄罗斯枪战二战电影-->movie	
组合条件搜索-->2019年电影中国大陆飞驰人生-->movie
组合条件搜索-->电影中国大陆2015年左耳-->movie-
组合条件搜索-->美国2018年死侍2我爱我家电影-->movi
组合条件搜索-->美国2017年电影动作-->movie
组合条件搜索-->2002年电影美国谍影重重-->movie
组合条件搜索-->美国2007年电影变形金刚-->movie
组合条件搜索-->昭和风格的日本音乐-->music
组合条件搜索-->迪迦奥特曼不要短视频也不要收费-->music
组合条件搜索-->粤语歌曲经典-->music
组合条件搜索-->美国的摇滚乐-->music
组合条件搜索-->上世纪的美国经典音乐-->music
组合条件搜索-->最近美国的热门歌曲-->music
组合条件搜索-->免费港台音乐-->music

此分类无需预期意图
"""

prompts = [propose_prompt,entity_prompt]

def initialize_conversation():
    global conversation

    template = """
    你是一个影视、音乐知识搜索助手，必须按我的要求编写和标注一些对影视域相关的测试集
    1.每次生成的都不与上一次的重复,即使有重复也要保证相似度不超过10%.
    2.每个分类每次需要生成10组.
    3.生成的格式应为：分类-->测试语料-->分域(分为:AppControl?channel?command?movie?music)-->预期意图.
    4.按照用户给的分类实例,实例只能用作格式参考,实例只是告诉你我想表达的意思，不可以照抄.
    5.注意生成的一定要是真实存在的
    6.不要markdown格式,并且不要生成序列，分类之间不需要空白行
    7.对于AppControl领域,你只需要在bilibili,华数鲜时光,酷喵影视,爱奇艺,芒果tv,网易云,QQ音乐这几个APP徘徊
    {chat_history}
    用户: {input}
    你的回复:
    """

    prompt = PromptTemplate(
        input_variables=["chat_history", "input"], 
        template=template
    )

    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_BASE_URL,
        api_version=OPENAI_API_VERSION,
        deployment_name=AZURE_DEPLOYMENT_MODEL,
        openai_api_key=AZURE_OPENAI_API_KEY,
    )

    memory = ConversationBufferWindowMemory(return_messages=True, memory_key="chat_history", k=2)

    conversation = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=True
    )

def AzureChat_reponse(query:str):
    global conversation

    if conversation is None:
        initialize_conversation()

    result = conversation.predict(input=query)
    return result

import os

def save_to_excel(data, filename):
    df = pd.DataFrame(data.split('\n'), columns=['A'])
    if not os.path.isfile(filename):
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
    else:
        with pd.ExcelWriter(filename, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

for i in range(400):  
    prompt = prompts[i // 50]
    result = AzureChat_reponse(prompt)
    save_to_excel(result, 'result.xlsx')
    print(result)
