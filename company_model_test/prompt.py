import time
# from utils import BaseModel
import requests
import json
import openpyxl
import os
import re

class BaseModel:
    def request(self, question):
        raise NotImplementedError

class Model(BaseModel):
    # url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={}'
    headers = {"Content-Type": "application/json"}
    API_KEY = "yR9tCQUh4PzdRBjLl5EMfrxU"
    SECRET_KEY = "Gw1zAXQm4pZrug91IIa97L8I9GtmUA0a"

    def __init__(self):
        self.url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={}'.format(self.get_access_token())

    def __str__(self):
        return '文心一言4.0'

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        # print(str(requests.post(url, params=params).json().get("access_token")))
        return str(requests.post(url, params=params).json().get("access_token"))

    def request(self, question):
        max_retries = 5  # 最大重试次数，可以根据需要调整
        retries = 0
        while retries < max_retries:
            try:
                messages = []
                messages.append({'role': 'user', 'content': question})
                payload = {
                    "messages": messages,
                    "stream": False,
                    "user_id": "1001"
                }
                response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
                # print(json.loads(response.content)['result'])
                # print('-'*100)
                return json.loads(response.content)['result']
            except Exception as e:
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


video_file = "douban.xlsx"
music_file = "music.xlsx"
video_wb = openpyxl.load_workbook(video_file)
music_wb = openpyxl.load_workbook(music_file)

video_ws = video_wb.active
music_ws = music_wb.active


output_file = "prompt.xlsx"

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

current_row = 1
# current_row = ws.max_row + 1

def create_query(current_row):
    video_cell = video_ws.cell(row=current_row, column=1)
    music_cell = music_ws.cell(row=current_row, column=1)
    if video_cell.value == None or music_cell.value == None:
        return None
    video_question = re.sub(r'\n', ' ', str(video_cell.value))
    music_question = re.sub(r'\n', ' ', str(music_cell.value))
    return video_question,music_question

def create_actor(current_row):
    actor_video_cell = video_ws.cell(row=current_row, column=2)
    actor_music_cell = music_ws.cell(row=current_row, column=2)
    if actor_video_cell.value == None or actor_music_cell == None:
        return None
    actor_video = re.sub(r'\n', ' ', str(actor_video_cell.value))
    actor_music = re.sub(r'\n', ' ', str(actor_music_cell.value))
    return actor_video,actor_music

def save_to_excel(result, current_row):
    for line in result.split('\n'):
        ws.cell(row=ws.max_row + 1, column=1, value=line)
        # current_row += 1
    # save_current_row += 1
    current_row +=1  
    wb.save(output_file)
    return current_row

if __name__ == "__main__":
    while True:
        video,music = create_query(current_row)
        video_actor,music_actor = create_actor(current_row)

        ##多个实体
        if video == None or music == None:
            break

        # template = f"""
        # 对于以下实体以及人，帮我按照多个实体规则，泛化出新的实体.
        # 输出请按照以下格式：
        # 泛化类型-->泛化-->实体-->movie/music
        # 则你的回答应该是：多个实体-->周杰伦青花瓷-->青花瓷
        # 能带动词就带动词，例如看，听，放，去等等
        # 需要你泛化的实体如下：
        # 影视：{video}-->{video_actor}
        # 音乐：{music}-->{music_actor}
        # 而你的回答格式应该是：
        # 多个实体-->{video_actor}{video}-->{video}-->movie
        # 多个实体-->{music_actor}{music}-->{music}-->music

        # 限制：必须按照格式进行
        # """

        ##实体少字/多字
        # template = f"""
        # 对于以下实体，帮我按照实体少字/多字规则，泛化出新的实体.
        # 输出请按照以下格式：泛化类型-->泛化-->实体-->movie/music
        # 例如：
        # 实体少字/多字-->汤姆故事乐园-->汤姆猫故事乐园
        # 实体少字/多字-->马克的医院-->马克的宠物医院
        # 实体少字/多字-->看广卫视-->看广东卫视
        # 能泛化的泛化，如果你认为泛化不了可以跳过，音乐名如果是一个字的就增一个字，例如：实体少字/多字-->等等-->等-->music
        # 影视如果是带续传的，则减或增主体的字，例如：实体少字/多字-->庆余第一季-->庆余年第一季-->movie
        # 需要你泛化的实体如下：
        # 影视：{video}
        # 音乐：{music}
        # 而你的回答格式应该是：
        # 实体少字/多字-->泛化(应该少了或多了1-2个字，此括号是提示无需输出)-->正确片名-->movie
        # 实体少字/多字-->泛化(应该少了或多了1-2个字，此括号是提示无需输出)-->正确音乐名-->music
        # 注意：每个回答一行，一次泛化里只允许少1-2个字,如果出现某部影片的续传，例如：复仇者联盟3，则少字的时候这个3是不能消失的，正确示范：实体少字/多字-->复仇联盟3-->复仇者联盟3

        # 限制：必须按照格式进行
        # """

        ## 实体重叠
        # template = f"""
        # 对于以下实体，帮我按照实体重叠规则，泛化出新的实体.
        # 输出请按照以下格式：泛化类型-->泛化-->实体-->movie/music
        # 例如：
        # 实体重叠-->汤姆猫故事乐园汤姆猫故事乐园-->汤姆猫故事乐园
        # 实体重叠-->马克的宠物医院马克的宠物医院-->马克的宠物医院
        # 实体重叠-->看广东卫视看广东卫视-->看广东卫视
        # 实体重叠-->起风了起风了-->起风了
        # 能带动词就带动词，例如看，听，放，去等等
        # 需要你泛化的实体如下：
        # 影视：{video}
        # 音乐：{music}
        # 而你的回答格式应该是：
        # 实体重叠-->{video}{video}-->{video}-->movie
        # 实体重叠-->{music}{music}-->{music}-->music

        # 限制：必须按照格式进行
        # """

        # ##实体颠倒
        # template = f"""
        # 对于以下实体影片，帮我按照实体颠倒规则，泛化出新的实体.
        # 输出请按照以下格式：泛化类型-->新的实体-->实体影片
        # 正确例子：
        # 实体颠倒-->故事乐园汤姆猫-->汤姆猫故事乐园
        # 实体颠倒-->宠物医院马克的-->马克的宠物医院
        # 实体颠倒-->看卫视广东-->看广东卫视
        # 错误例子：实体颠倒-->叠击影狙-->叠影狙击，这种不符合人类说话风格，，正确的应该是实体颠倒-->叠影狙击-->狙击叠影
        # 但是不适合泛化或者你认为泛化出来的实体正常人不会这样说的，可以不输出，不要生成错误的例子
        # 需要你泛化的实体影片如下：
        # {video}
        # 限制：必须按照格式进行
        # """

        ## 实体错字
        # template = f"""
        #     对于以下实体，帮我按照实体错字规则，泛化出新的实体.
        #     输出请按照以下格式：泛化类型-->错字片名->正确片名-->movie/music
        #     不要用谐音和读音一样的字，例如：长江期号（原片名长江七号）.
        #     而且尽量保证一个实体里只有一到两个错字.
        #     例如：
        #     实体错字-->播放深情宝贝-->神奇宝贝
        #     实体错字-->长江鸡号-->长江七号
        #     实体错字-->失坑玩家-->失控玩家
        #     实体错字-->谋杀小说家-->刺杀小说家
        #     实体错字-->烂滴她-->灿烂的她灿
        #     实体错字-->惊花瓷-->青花瓷
        #     实体错字-->还是很惨你-->还是很想你
        #     实体错字-->垫底狼妹-->垫底辣妹
        # 能带动词就带动词，例如看或者听
        # 需要你泛化的实体如下：
        # {video}，{music}
        # 而你的回答格式应该是：
        # 实体错字-->盗梦可间-->盗梦空间
        # 实体错字-->下苹果-->小苹果

        # 限制：必须按照格式进行
        # """

        # # 实体别名
        # template = f"""
        #     对于以下实体，帮我按照实体别名规则，泛化出新的实体.
        #     输出请按照以下格式：泛化类型-->实体别名->实体片名
        #     实体别名类似于简称
        #     例如：
        #     实体别名-->我想看美队3-->美国队长3
        #     实体别名-->星战4播放-->星球大战4
        #     实体别名-->指环王3-->指环王王者无敌
        #     实体别名-->播放死亡圣器-->哈利·波特与死亡圣器
        #     实体别名-->打开跑男第二季-->奔跑吧兄弟第二季
        #     实体别名-->播放藏不住-->偷偷藏不住
        #     实体别名-->大侦探9-->大侦探第九季
        #     实体别名-->斗破-->斗破苍穹
        # 能带动词就带动词
        # 需要你泛化的实体如下：
        # 影视：{video}
        # 音乐：{music}
        # 而你的回答格式应该是：
        # 实体别名-->XXX-->XXX-->movie
        # 实体别名-->XXX-->XXX-->music

        # 限制：必须按照格式进行
        # """

        # 语句乱序
        template = f"""
            对于以下实体，帮我按照语句乱序规则，泛化出新的实体.
            输出请按照以下格式：语句乱序-->实体别名->实体片名-->movie/music
            语句乱序相当于再不影响其意思理解的情况下主谓宾调换
            例如：
            语句乱序-->动作片2021年播放的-->2021年播放的动作片-->movie
            语句乱序-->2021年动作片播放-->播放2021年动作片-->movie
            语句乱序-->新生最新电视剧-->最新电视剧新生-->movie
            语句乱序-->播放青花瓷周杰伦唱的-->播放周杰伦唱的青花瓷-->music
            语句乱序-->免费播放经典的电影-->播放免费经典的电影-->movie
            语句乱序-->青花瓷周杰伦唱的我想听-->我想听周杰伦唱的青花瓷-->movie
            语句乱序-->电视剧刘德华主演的播放-->播放刘德华主演的电视剧-->movie
        能带动词就带动词
        需要你泛化的实体如下：
        影视：{video}, 影视作者：{video_actor}
        音乐：{music}, 音乐作者：{music_actor}
        而你的回答格式应该是：
        语句乱序-->XXX-->XXX-->movie
        语句乱序-->XXX-->XXX-->music

        限制：必须按照格式进行
        """

        baidu = Model()
        print(template)
        result = baidu.request(template)
        print(result)
        current_row = save_to_excel(result, current_row)