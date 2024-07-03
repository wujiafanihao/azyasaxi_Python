prompt = '''
你是一位友好的人工智能
'''

query = '''
hi
'''

from gpt4o_model import OPENAI


def response(prompt,query):
    gpt4o = OPENAI()
    result = gpt4o.gpt_4o_request(prompt,query)
    return result

gpt4o_response = response(prompt,query)
print(gpt4o_response)

