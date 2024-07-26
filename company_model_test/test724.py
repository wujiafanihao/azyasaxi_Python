from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

file_path = 'test0724.xlsx'
output_file = 'Answer.xlsx'

def create_query(file_path):
    df = pd.read_excel(file_path, index_col=False, header=None)
    a_col = df[0].astype(str).dropna()
    c_values = ['的主演是谁', '的导演是谁', '讲什么的', '哪一年的', '的剧情简介']
    
    results = []

    for a_value in a_col:
        for c_value in c_values:
            results.append(a_value + c_value)

    return results

template = """
You are a helpful assistant that answers the user 's question : {query}

user : {query}
AI:
"""

def init_model(query: str):
    prompt = PromptTemplate(template=template, input_variables=['query'])
    llm = AzureChatOpenAI(
        temperature=0,
        azure_deployment='tcl-gpt4o1'
    )
    llm_chain = LLMChain(
        prompt=prompt,
        llm=llm,
        verbose=True
    )

    result = llm_chain.invoke({
        "query": query
    })
    return result

def save_to_excel(query, answer, file_name):
    if not os.path.isfile(file_name):
        df = pd.DataFrame(columns=['query', 'answer'])
    else:
        df = pd.read_excel(file_name)
    
    new_data = pd.DataFrame({
        'query': [query],
        'answer': [answer]
    })
    
    df = pd.concat([df, new_data], ignore_index=True)
    
    df.to_excel(file_name, index=False)

queries = create_query(file_path)
for query in queries:
    response = init_model(query)
    print(response)
    save_to_excel(response['query'], response['text'], output_file)
