import time
# from utils import BaseModel
from openai import OpenAI
import requests
import json

import openpyxl
import os
import re

input_file = "LLAMA3.xlsx"
output_file = "baichuan4_content.xlsx"
current_row = 2
sheet_index = 4
input_wb = openpyxl.load_workbook(input_file)
input_ws = input_wb.worksheets[sheet_index]
title_cell = input_ws.cell(row=2, column=1)
Model = "baichuan4"
title = str(title_cell.value)

if not os.path.exists(output_file):
    wb = openpyxl.Workbook()
    # 创建第一个新的表单
    ws1 = wb.create_sheet(title='Sheet1')
    ws = wb.create_sheet(title=f"{title}_{Model}")
    ws["A1"] = "Domain"
    ws["B1"] = "Model"
    ws["C1"] = "Question"
    ws['D1'] = "PromptQuestion"
    ws['D1'] = "Score"
    ws["E1"] = "Model Answer"
    ws['F1'] = "Evaluation Result"
    wb.save(output_file)
else:
    wb = openpyxl.load_workbook(output_file)
    ws = wb.active


class BaseModel:
    def request(self, question):
        raise NotImplementedError

# 文心一言4.0  chat_wenxin
class baichuan4(BaseModel):
    def __init__(self):
        self.API_KEY = "sk-2b992e6d048a619c4fb127f2579cad6c"
        #self.url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_3_8b?access_token={}'.format(self.get_access_token())
    # url = 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={}'
      #

    #SECRET_KEY = "43kNUUdLd3PotGSiABq8ByRvudEW6j23"





    def __str__(self):
        return 'baichuan4'

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
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.API_KEY}
        max_retries = 5  # 最大重试次数，可以根据需要调整
        retries = 0
        while retries < max_retries:
            try:
                messages = []
                # messages.append({"role": "system", "content": "你是一个人工智能助手"})
                messages.append({'role': 'user', 'content': question})
                # payload = {
                #     "messages": messages,
                #     "stream": False,
                #     "user_id": "1001"
                # }
                #response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
                client = OpenAI(api_key=self.API_KEY, base_url="https://api.baichuan-ai.com/v1/")
                response = client.chat.completions.create(
                    model="Baichuan4",
                    messages=messages
                )
                # print(json.loads(response.content)['result'])
                # print('-'*100)
                print(response.choices[0].message.content)
                return response.choices[0].message.content#json.loads(response.choices[0].message.content)
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
    question_cell = input_ws.cell(row=current_row, column=3)
    if question_cell.value == None:
        return None
    question = re.sub(r'\n', ' ', str(question_cell.value))
    return question

i = 2
if __name__ == '__main__':
    while True:
        dp = baichuan4()
        query = create_query(current_row)
        if query == None:
            sheet_index +=1
            current_row = 2
            i = 2
            title_cell = input_ws.cell(row=2, column=1)
            ws = wb.create_sheet(title=f"{title}_{Model}")
            ws["A1"] = "Domain"
            ws["B1"] = "Model"
            ws["C1"] = "Question"
            ws['D1'] = "PromptQuestion"
            ws['D1'] = "Score"
            ws["E1"] = "Model Answer"
            ws['F1'] = "Evaluation Result"
            if sheet_index >= 8:
                break
            input_ws = input_wb.worksheets[sheet_index]
            continue
        question = query
        print(question)
        result = dp.request(question)

        Domain_cell = input_ws.cell(row=current_row, column=1)
        question_cell = input_ws.cell(row=current_row, column=3)
        rect_answer_cell = input_ws.cell(row=current_row, column=6)

        Domain = ws.cell(row=current_row, column=1, value=Domain_cell.value)
        model = ws.cell(row=current_row, column=2, value="baichuan4")
        question = ws.cell(row=current_row, column=3, value=question_cell.value)
        result_cell = ws.cell(row=ws.max_row,column=6,value=result)

        print(f"Chat_BOT: {result}")
        wb.save(output_file)
        print(f"第{i}题已成功存储至 Excel 文件中，结果为：{result}")
        current_row += 1
        i+=1
        time.sleep(5)
