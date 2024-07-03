import time
# from utils import BaseModel
from openai import OpenAI
import requests
import json
import openpyxl
import os
import re

input_file = "douban.xlsx"
output_file = "douban_answer.xlsx"
input_wb = openpyxl.load_workbook(input_file)
input_ws = input_wb.active

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

current_row = ws.max_row + 1

class BaseModel:
    def request(self, question):
        raise NotImplementedError

# 文心一言4.0  chat_wenxin
class deepseek(BaseModel):
    # url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={}'
    headers = {"Content-Type": "application/json"}   #

    #SECRET_KEY = "43kNUUdLd3PotGSiABq8ByRvudEW6j23"


    def __init__(self):
        self.API_KEY = "sk-ab273b67e6e64f399870cf37b33cf34f"
        #self.url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_8b?access_token={}'.format(self.get_access_token())


    def __str__(self):
        return 'deepseek_v2'

    # def get_access_token(self):
    #     """
    #     使用 AK，SK 生成鉴权签名（Access Token）
    #     :return: access_token，或是None(如果错误)
    #     """
    #     url = "https://aip.baidubce.com/oauth/2.0/token"
    #     params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
    #     # print(str(requests.post(url, params=params).json().get("access_token")))
    #     return str(requests.post(url, params=params).json().get("access_token"))

    def request(self, question):
        max_retries = 5  # 最大重试次数，可以根据需要调整
        retries = 0
        while retries < max_retries:
            try:
                messages = []
                messages.append({"role": "system", "content": "你是一个人工智能助手"})
                messages.append({'role': 'user', 'content': question})
                # payload = {
                #     "messages": messages,
                #     "stream": False,
                #     "user_id": "1001"
                # }
                #response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
                client = OpenAI(api_key=self.API_KEY, base_url="https://api.deepseek.com")
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                # print(json.loads(response.content)['result'])
                # print('-'*100)
                # print(response.choices[0].message.content)
                response = response.choices[0].message.content
                return response#json.loads(response.choices[0].message.content)
            except Exception as e:
                print(e)
                retries += 1
                if retries == max_retries:  # 达到最大重试次数后抛出异常
                    print("Max retries reached. Unable to get a response for:", question)
                    print("Error:", str(e))
                    return ''
                print("Request failed. Retrying in 20 seconds...")
                time.sleep(20)

    def multiple_request(self, prompt):
        # 多轮对话由于模型自身最大token数限制
        # 大模型之间互相对话
        conversation_history = []

        # TODO  文心一言无法在对话首个位置进行角色限制,所以prompt需要加到每一句

        # prompt = '请对下列对话做出回答，要求：'
        # for index, (key, value) in enumerate(evaluation_criteria.items(), start=1):
        #     prompt += '{}.{}'.format(index, value)
        # conversation_history.append({'role': 'user', 'content': prompt})
        # answer = self.request(prompt)
        # conversation_history.append({'role': 'assistant', 'content': answer})

        def inner_function(question):
            max_retries = 5  # 最大重试次数，可以根据需要调整
            retries = 0
            nonlocal conversation_history
            while retries < max_retries:
                try:
                    # messages = []
                    if retries < 1:
                        conversation_history.append(
                            {'role': 'user', 'content': prompt + '问题：' + question + '，限制回答不超过50字,只需要一个回答'})
                    payload = {
                        "messages": conversation_history,
                        "stream": False,
                        "user_id": "1001"
                    }
                    response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
                    # print(json.loads(response.content)['result'])
                    # print('-'*100)
                    answer = json.loads(response.content)['result']
                    conversation_history.append({'role': 'assistant', 'content': answer})
                    print('文心一言4.0:{}'.format(conversation_history))
                    return answer, conversation_history
                except Exception as e:
                    print(str(e))
                    retries += 1
                    if retries == max_retries:  # 达到最大重试次数后抛出异常
                        print("Max retries reached. Unable to get a response for:", question)
                        print("Error:", str(e))
                        conversation_history.append({'role': 'assistant', 'content': ''})
                        return ''
                    print("Request failed. Retrying in 30 seconds...")
                    time.sleep(30)

        # Dialogue function's other logic
        # ...
        return inner_function

def create_query(current_row):
    current_row
    queries = []
    for row in range(current_row, current_row + 5):
        question_cell = input_ws.cell(row=row, column=1)
        # if question_cell.value is None:
        #     return None
        # if len(str(question_cell.value)) < 4:
        #     continue
        # if len(str(question_cell.value)) >= 4:
        if question_cell.value == None:
            break
        question = re.sub(r'\n', ' ', str(question_cell.value))
        queries.append(question)
    return queries

def create_actor(current_row):
    actors = []
    for row in range(current_row, current_row + 5):
        actor_cell = input_ws.cell(row=row, column=2)
        actor = re.sub(r'\n', ' ', str(actor_cell.value))
        actors.append(actor)
    return actors

def save_to_excel(result, current_row):
    for line in result.split('\n'):
        ws.cell(row=current_row, column=1, value=line)
        current_row += 1
    current_row += 1  
    wb.save(output_file)
    return current_row

if __name__ == '__main__':
    while True:
        baidu = deepseek()
        queries = create_query(current_row)
        actors = create_actor(current_row)
#         examples = [
#     '给我调一下色温(句式泛化)',
#     '进到那个U盘页面(句式泛化)',
#     '唱一个死了都要爱(句式泛化)',
#     '0到3岁动画片(句式泛化)',
#     '2020到2025年刘德华的电影(句式泛化)',
#     '帮我找一部国语版的赌侠周星驰演的(句式泛化)',
#     '背景架空的电影(句式泛化)',
#     '本月最新的电影(句式泛化)',
#     '播放老版西游记六小龄童主演的(句式泛化)',
#     '不要钱的动画电影而且是搞笑(句式泛化)',
#     '大家最喜欢的电影(句式泛化)',
#     '盗墓题材的电影(句式泛化)',
#     '豆瓣高分电影(句式泛化)',
#     '豆瓣上评分高的泰国电影(句式泛化)',
#     '逗比搞笑的电影(句式泛化)',
#     '放梅婷演的电影连续剧(句式泛化)',
#     '更多的阿贡(句式泛化)',
#     '美国九十年代的电影(句式泛化)',
#     '来一首英文的经典说唱(句式泛化)',
#     '最早的张艺谋导演的大红灯笼高高挂(句式泛化)',
#     '最近十年热门的电视剧(句式泛化)',
#     '最近十年评分最高的电视剧(句式泛化)',
#     '综艺歌手(句式泛化)',
#     '病变刘大拿唱的(语句乱序)',
#     '年会不能停播放(语句乱序)',
#     '就让这大雨全都落下汪苏泷唱的(语句乱序)',
#     '播放最新的电影(句式泛化)',
#    ' 查找周杰伦的专辑(句式泛化)',
#     '给我列出最近的热门电视剧(句式泛化)',
#     '推荐几首流行歌曲给我(句式泛化)',
#     '经典电影有哪些值得一看(语句乱序)',
#     '流行歌曲哪些比较火(语句乱序)',
# ]
        # examples = [
        #     '我想看冯绍峰的电影(垂域间多轮对话)',
        #     '搞错了冯小刚的(垂域间多轮对话)',
        #     '',
        #     '90年代的科幻片(垂域间多轮对话)',
        #     '还是80年代的吧(垂域间多轮对话)',
        #     '',
        #     '美国的科幻片(垂域间多轮对话)',
        #     '是悬疑片说错了(垂域间多轮对话)',
        #     '',
        #     '周润发的喜剧片(垂域间多轮对话)',
        #     '说错了是动作片(垂域间多轮对话)',
        #     '',
        #     '明天的天气怎么样(垂域间多轮对话)',
        #     '要看上海的(垂域间多轮对话)',
        #     '',
        #     '环大西洋电影(垂域间多轮对话)',
        #     '是太平洋我说错了(垂域间多轮对话)',
        #     '',
        #     '放首陈奕迅的你的背包(垂域间多轮对话)',
        #     '听胡彦斌的吧(垂域间多轮对话)',
        # ]

    #     words = """
    #     对于以下实体片名，帮我按照实体颠倒、谐音、多字、少字、重复等规则，泛化出新的实体片名，输出请按照以下格式：实体片名-->泛化片名(泛化类型)
    # 正确的例子：小猪佩奇-->佩奇小猪(实体颠倒)，小猪佩奇-->小小猪佩奇(多字)，小猪佩奇-->小猪佩奇小猪佩奇(重复)，小猪佩奇-->猪佩奇(少字)，中国人-->中国融(谐音),
    # 泰坦尼克号-->泰坦弥克号(谐音)，
    # 错误的例子：“叠影狙击-->叠击影狙（实体颠倒），这种不符合人类说话风格，正确的应该是叠影狙击-->狙击叠影（实体颠倒）”
    # 记住：每个实体都尽量泛化输出上面的几种类型
    # 但是不适合泛化或者你认为泛化出来的实体正常人不会这样说的，可以不输出

    # 需要你泛化的实体如下：
    # {}
    #     """.format('\n'.join(queries))
        # words= """
        # 对于以下例子，帮我按照语句乱序和句式泛化，生成出新的实体，输出请按照以下格式：泛化实体(泛化类型)
        # 例如：给我调一下色温(句式泛化)，刘大拿唱的病变-->病变刘大拿唱的(语句乱序).
        # 注意：句式泛化不需要全部按照实体片名来，你可靠自由想象发挥，但是都是要与影视或者音乐相关，
        # 语句乱序也必须要与影视或者音乐相关，切记乱序后意思是要能读懂的。
        # 泛化类型必须遵循我提供的上面两种类型,而且不能有指代的关系，例如：听听那首老歌(句式泛化)，帮我搜索那部经典电影(句式泛化)，
        # 我希望要有精确地剧名以及音乐名。
        # 不适合泛化或者你认为泛化出来的实体正常人不会这样说的，可以不输出，不能浮夸,人名不可出现（李易峰，吴亦凡，范冰冰，柯震东，房祖名，王力宏，李云迪）这些人名
        # 以下是泛化实体的例子：
        # {}
        # 只需要生成十条,我希望跟你根据例子自己想(演员)，(歌手)，(剧名)，(歌名),不要重复例子里出现的歌手演员.
        # """.format('\n'.join(examples))
        # words= """
        # 对于以下实例，帮我按照垂域间多轮对话，生成出新的多轮对话，输出请按照以下格式：泛化实体(泛化类型)
        # 例如：
        # 第一轮：我想看冯绍峰的电影(垂域间多轮对话)
        # 第二轮：搞错了冯小刚的(垂域间多轮对话)
        # 第一轮：90年代的科幻片(垂域间多轮对话)
        # 第二轮：还是80年代的吧(垂域间多轮对话)
        # 注意：垂域间多轮对话不允许全部按照实例来，你可靠自由想象发挥，但是都是要与影视或者音乐相关，以及影视，
        # 泛化类型必须遵循我提供的上面类型,而且不能有指代的关系，例如：听听那首老歌(句式泛化)，帮我搜索那部经典电影(句式泛化)，
        # 我希望要有精确地剧名以及音乐名，以及这次生成的是多轮纠错
        # 不适合泛化或者你认为泛化出来的实体正常人不会这样说的，可以不输出，
        # 不能浮夸,人名不可出现（李易峰，吴亦凡，范冰冰，柯震东，房祖名，王力宏，李云迪）这些人名
        # 以下是垂域间多轮对话实例：
        # {}
        # 记住每一二轮为一组，每组一个换行隔开
        # """.format('\n'.join(example))
        words= f"""
        请根据以下指示生成知识问答内容，并确保内容的真实性和创造性。输出格式如下：
        外部服务内容是：提供一些背景信息或上下文(可以带符号)-->用户的问题(注意不要带任何符号，包括书名号)-->将用户的问题或请求转化为更明确的指令(注意不要带任何符号，包括书名号)。

        示例：
        外部服务内容是：《惜花芷》的女主是花芷。你喜欢看古言小说吗？我也很喜欢呢-->是谁演的-->《惜花芷》的女主是花芷是谁演的
        外部服务内容是：我不太清楚“背着善宰跑”是什么剧情的电视剧呢，我平时喜欢看一些青春校园剧，你有兴趣吗？-->直接搜这个-->直接搜背着善宰跑
        外部服务内容是：《甄嬛传》是一部宫斗类型的电视剧。-->播这个的主题曲-->播放甄嬛传的主题曲
        外部服务内容是：《甄嬛传》是一部宫斗类型的电视剧。-->播这个的片尾曲-->播放甄嬛传的片尾曲
        提供的实体片名:
        {queries}

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
        提供的演员:
        {actors}

        我需要你生成十组,五组为实体片名，五组为演员
        用户的问题和将用户的问题或请求转化为更明确的指令这两步不要带有标点符号
        每组一个换行隔开，生成的内容应符合上述格式和要求。
        """

        print(words)
        if queries is None:
            break
        result = baidu.request(words)

        print(result)
        current_row = save_to_excel(result, current_row)
        print(queries)
