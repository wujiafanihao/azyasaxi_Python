from langchain_openai import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import HumanMessage,AIMessage
from dotenv import load_dotenv
load_dotenv()

from langchain.serpapi import SerpAPIWrapper
search = SerpAPIWrapper()

from langchain.agents import Tool,initialize_agent,AgentType

search_tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    )
]

llm = ChatOpenAI(temperature=0,verbose=True,streaming=True,callbacks=[StreamingStdOutCallbackHandler()])
memory = ConversationSummaryBufferMemory(llm=llm,memory_key="chat_history",return_messages=True,verbose=True)
agent = initialize_agent(tools=search_tools,llm=llm,memory=memory,agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,verbose=True)

while True:
    user_input = input("User: ")
    Messages = [HumanMessage(content=user_input)]
    agent.run(f"Qwen：{Messages}")


