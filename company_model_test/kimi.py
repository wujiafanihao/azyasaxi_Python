import time
# from utils import BaseModel
import requests
import os
import openpyxl
import re
import json

input_file = "LLAMA3.xlsx"
output_file = "Model Answer.xlsx"

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"] = "Model Answer"
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active

current_row = 2
sheet_index = 11
# result = []

class BaseModel:
    def request(self, question):
        raise NotImplementedError

# 文心一言4.0  chat_wenxin
class ModelWenXinYiYan4(BaseModel):
    # url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={}'
    headers = {"Content-Type": "application/json"}   #
    API_KEY = "17nuou6Z2Ao5REPpYwLzZ2QF"
    SECRET_KEY = "43kNUUdLd3PotGSiABq8ByRvudEW6j23"

    def __init__(self):
        self.url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_8b?access_token={}'.format(self.get_access_token())

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

i = 2
if __name__ == '__main__':
    while True: 
        input_wb = openpyxl.load_workbook(input_file)
        input_ws = input_wb.worksheets[sheet_index]

        question_cell = input_ws.cell(row=current_row, column=3)
        question = re.sub(r'\n', ' ', str(question_cell.value))
        print(question)
        if question == None:
            print("C列已结束，程序退出。")
            break
        # .Remember: You must answer in Chinese.
        #,demand:[You only tell me A or B or C or D]
        baidu = ModelWenXinYiYan4()
        result = baidu.request(question + ',demand:[You only tell me A or B or C or D]')
        match = re.search('[A-D]', result)
        # nest_result = ws.cell(row=ws.max_row + 1, column=1, value=result)
        print(f"第{i}题")
        if i == 22:
            print("结束循环")
            break
        if match:
            option_result = ws.cell(row=ws.max_row + 1, column=1, value=match.group())
            print(result)
            wb.save(output_file)
            print("已成功存储至 Excel 文件中。",option_result)
            current_row += 1
            i += 1


        # print(result)
        # content_result = ws.cell(row=ws.max_row + 1, column=1, value=result)
        # wb.save(output_file)
        # print("已成功存储至 Excel 文件中。",content_result)
        # current_row += 1
        
        
