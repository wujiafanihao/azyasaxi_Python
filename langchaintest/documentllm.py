from dotenv import load_dotenv
load_dotenv()
import bs4
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.documents import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains.retrieval import create_retrieval_chain

# 获取网页内容
def get_documents_from_web(url):
    loader = WebBaseLoader(url)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    solitDocs = splitter.split_documents(docs)
    return solitDocs

# def create_vector(docs):
#     embedding = OpenAIEmbeddings()
#     vectorStore = FAISS.from_documents(docs,embedding=embedding)
#     return vectorStore

# def create_chain(vectorStore):
    retriever = vectorStore.as_retriever()

    retriever_chain = create_retrieval_chain(
        retriever,
        chain
    )

    return retriever_chain

web_path = "https://lilianweng.github.io/posts/2023-06-23-agent/"
docs = get_documents_from_web(web_path)
# vectorStore = create_vector(docs)
# chain = create_chain(vectorStore)

# docA = Document(
#     page_content="LangChain is a framework for developing applications powered by large language models (LLMs)."
# )

# 模型
model = ChatOpenAI(
    temperature=0,
    verbose=True,
)
# prompt
prompt = ChatPromptTemplate.from_template("""
    Answer the user's question. 
    Context: {context}
    Question: {question}
""")

chain = prompt | model
chain = create_stuff_documents_chain(
    llm=model,
    prompt=prompt,
)

while True:
    query = input("Human：")
    if query == "exit":
        break
    response = chain.invoke({
        "question":query,
        "context":docs
        })
    print(f"AI：{response}")