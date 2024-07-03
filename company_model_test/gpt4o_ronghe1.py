from gpt4o_model import OPENAI

prompt = '''
    你是一个影视、音乐、百科问答等知识搜索助手，必须按我的要求回答问题,
    根据我下面给你的作者以及代表作，按照以下标准回复格式进行回复，请使用中文回复！
    记住{author_info}和{work_info}是由你来生成,然后回答抽取的{work}不超过五个，
    {plots}我希望详细一点,表述需要变化风格，并且我希望里面能出现{Characters appearing in the plot}.
    注意{character}一定要是详情的，不能用"重要角色","男主角","女主角"等一些含糊的指代来代替.
    用户请求只需要提及一个{character}，标注回答也只需要提及一个{《work}》}.

    假设用户提供：
    作者：{author}
    代表作：{works}

    一定要遵循格式下面格式生成：
    {*}这个属于变量符号,*为变量名，无须将变量名以及变量符号生成出来.
    
    标准回复格式：类型一定要按照{请求助理},{用户请求},{标注回答}.
    
    请求助理：外部服务内容是：{author}，{author_info} (几几年出生，哪里人等等的信息)

- **《{work}》系列**：{author}在里面{action?担任:扮演}{character},{work_info}以及{plots}。

- **《{work}》系列**：{author}在里面扮演{action?担任:扮演}{character},{work_info}以及{plots}。

- **《{work}》系列**：{author}在里面扮演{action?担任:扮演}{character},{work_info}以及{plots}。

    用户请求：{action?看:打开:播放:搜索}{Characters appearing in the plot}。

    标注回答：{action?看:打开:播放:搜索}{《work}》}。

    '''

import pandas as pd

file_path = 'Actor.xlsx'
def read_actor_info(file_path):
    df = pd.read_excel(file_path, header=None)
    return df

def get_actor_info(df,index):
    row = df.iloc[index]
    actor_name = row[0]
    works = row[1:].dropna().tolist()
    
    return actor_name,works

def parse_result(result):
    try:
        request_assistants = result.split('用户请求：')[0]
        request_assistants = request_assistants.split('请求助理：')[1]
    except Exception as e:
        request_assistants = ""
        print(f"Error parsing request_assistants: {e}")
    try:
        user_request = result.split('用户请求：')[1]
        user_request = user_request.split('标注回答：')[0]
    except Exception as e:
        user_request = ""
        print(f"Error parsing user_request: {e}")

    try:
        labeled_response = result.split('标注回答：')[1]
    except Exception as e:
        labeled_response = ""
        print(f"Error parsing labeled_response: {e}")

    return request_assistants, user_request, labeled_response

if __name__ == '__main__':
    df = read_actor_info(file_path)
    index = 0
    gpt4o = OPENAI()


    result_df = pd.DataFrame(columns=['请求助理', '用户请求', '标注回答'])
    while True:

        actor_name,works = get_actor_info(df,index)

        if pd.isna(actor_name):
            break

        i = ""
        for work in works:
            a = 0
            i += work + ", " 

        query = f"""
        作者：{actor_name}
        代表作(每个作品都是逗号隔开)：{i}
        """

        print(query)
        result = gpt4o.gpt_4o_request(prompt,query)
        print(result)
        request_assistants,user_request, labeled_response = parse_result(result)
        print(f"request_assistants = {request_assistants}.\nuser_request={user_request}.\nlabeled_response={labeled_response}")

        new_row = pd.DataFrame({
                '请求助理': [request_assistants],
                '用户请求': [user_request],
                '标注回答': [labeled_response]
        })
        result_df = pd.concat([result_df, new_row], ignore_index=True)

        try:
            with pd.ExcelWriter('results.xlsx', mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                new_row.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row, columns=['请求助理', '用户请求', '标注回答'])
        except FileNotFoundError:
            new_row.to_excel('results.xlsx', index=False, columns=['请求助理', '用户请求', '标注回答'])

        index += 1
