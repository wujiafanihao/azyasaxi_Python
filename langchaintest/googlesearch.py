from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent,AgentType,load_tools

llm = ChatOpenAI()

tools = load_tools(["serpapi", "llm-math"],llm=llm)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# agent.run("What is langchain?")
response = llm.invoke("What is langchain?")
print(response.content)