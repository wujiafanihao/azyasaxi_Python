from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversation.base import ConversationChain
from langchain_community.document_loaders.pdf import PyPDFLoader

def get_document_based_on_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pdf = loader.load()
    return pdf

llm = ChatOpenAI(
    temperature=0,
    verbose=True,
    streaming=True,
    max_tokens=500,
    callbacks=[StreamingStdOutCallbackHandler()]
)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You is a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}"),
])

memory = ConversationBufferWindowMemory(
    memory_key="history",
    k=5,
    return_messages=True
)

conversation_chain = ConversationChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

while True:
    user_input = input("user:")
    print("Mistral:",end="")
    response = conversation_chain.invoke({
        "input":user_input,
        "history":[]
        })
    print('\n')

    # print(f"Mistral:{response.content}")