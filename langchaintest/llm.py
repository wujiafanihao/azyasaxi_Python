from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain_community.chat_models import ChatOpenAI
from langchain import LLMChain,PromptTemplate
from langchain.schema import HumanMessage,SystemMessage

def track_tokens_usage(chain,query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f"Total tokens:{cb.total_tokens}")

    return result

import os
load_dotenv()

template = """
你只能回答中文.
{chat_history}
Human: {human_input}
Ai:"""
prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], 
    template=template
)


model = os.environ.get("OPENAI_MODEL")

llm = ChatOpenAI(temperature=0,model=model,verbose = True)

llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=ConversationBufferMemory(memory_key="chat_history"),
)

while True:
    query = input("Human:")
    if query == "/bye":
        break
    content = str([SystemMessage(content="你只能用英语回答"),
        HumanMessage(content=query)])
    response = track_tokens_usage(llm_chain, content)
        
    print(f"Ai: {response}")

