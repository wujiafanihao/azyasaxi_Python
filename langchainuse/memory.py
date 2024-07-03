from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
from dotenv import load_dotenv

load_dotenv()

template = """You are a chatbot having a conversation with a human.

{chat_history}

Human: {human_input}
Chatbot:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"], template=template
)

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=OpenAI(),
    prompt=prompt,
    verbose=True,
    memory=memory,
)

llm_chain.predict(human_input="Hi there my friend")

llm_chain.predict(human_input="Not too bad - how are you?")

