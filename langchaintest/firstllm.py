from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain.schema import HumanMessage

model = ChatOpenAI(
    temperature=0.7,
    verbose=True,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "{input}"),
])

chain = prompt | model

def track_tokens_usage(chain,query):
    with get_openai_callback() as cb:
        chain.invoke(query)
        print(f"tokens used: {cb.total_tokens}")

while True:
    query = input("Human：")
    if query == "exit":
        break
    human_message = str(HumanMessage(content=query).content)
    print(human_message)
    track_tokens_usage(chain,human_message)
    response = chain.stream(human_message)
    for chunk in response:
        print(chunk.content,end="",flush=True)
    print("\n")