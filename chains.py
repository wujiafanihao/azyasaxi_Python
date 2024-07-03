from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate,MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.base import ConversationChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessageChunk
import os

# def get_document_basedon_pdf(file_path):
.#     docs = loader.load()
#     splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=10)
#     splitterPdf = splitter.split_documents(docs)
#     return splitterPdf

# def get_first_pdf_file(directory):
#     for filename in os.listdir(directory):
#         if filename.endswith(".pdf"):
#             return os.path.join(directory, filename)
#     return 'langchain.pdf'

# docs = get_document_basedon_pdf(get_first_pdf_file("uploads"))

# def create_db(pdf):
#     embeddings=OllamaEmbeddings(model="nomic-embed-text")
#     vectorStore = Chroma.from_documents(
#         pdf,embedding=embeddings,persist_directory ="chroma"
#     )
#     return vectorStore
# retriever = create_db(docs).as_retriever(search_kwargs={'k': 4})

# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)

# template = "anser the user's question based on the following context: {context}"

# RAG_prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template(template),
#     HumanMessagePromptTemplate.from_template("{input}")
# ])
common_prompt=ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])
llm = ChatOpenAI(temperature=0, streaming=True)
memory = ConversationBufferWindowMemory(return_messages=True,k=5,memory_key="history")

# retriever_chain = (
#         {"context": retriever | format_docs, "input": RunnablePassthrough()}
#         | RAG_prompt
#         | llm
#         | StrOutputParser()
# )

conversation_chain = ConversationChain(
    prompt=common_prompt,
    llm=llm,
    memory=memory,
    verbose=True,
)

generated_texts = []

def serialize_aimessagechunk(chunk):
    if isinstance(chunk,AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk.__name__)} is not a AIMessageChunk."
        )

async def text_generate_model(question):
    async for event in conversation_chain.astream_events(question,version="v1"):
        if event["event"] == "on_chat_model_stream":
            chunk_content = serialize_aimessagechunk(event["data"]["chunk"])
            generated_texts.append(chunk_content)
            yield f"{chunk_content}"
        elif event["event"] == "on_chat_model_end":
            print("Chat model has completed its response.")

# async def docs_generate_model(question):
#     async for chunk in retriever_chain.astream(question):
#         yield f"{chunk}"
                   

