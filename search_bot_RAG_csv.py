from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessageChunk
from langchain_openai import ChatOpenAI

csv_files = ['new.csv', 'hacker.csv']
# 加载CSV文件
def get_csv_to_vectorstore(csv_files:list):
    all_documents = []
    for file_path in csv_files:
        try:
            loader = CSVLoader(file_path=file_path, encoding='utf-8')
            documents = loader.load()
            all_documents.extend(documents)
        except Exception as e:
            try:
                loader = CSVLoader(file_path=file_path, encoding='gbk')
                documents = loader.load()
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    # 分割文档
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_documents = text_splitter.split_documents(all_documents)
    return split_documents

ack_knowledge = get_csv_to_vectorstore(csv_files)

def create_db(ack_knowledge:list):
    # 创建嵌入
    embeddings = OpenAIEmbeddings(base_url='https://api.chatanywhere.tech/v1/', api_key='sk-dw366zNMWe7tTmmRfzr0NTVMCjegXOCTU1PRdT3wTFvHjr4X', model='text-embedding-ada-002')

    # 创建向量存储
    vectorstore = FAISS.from_documents(ack_knowledge, embeddings)
    vectorstore.save_local("faiss_index")
    return vectorstore


# 创建自定义提示模板
template = """
从现在开始你是用户们的网站向导，你了解AI的实时新闻，包括一些其他领域的新闻，你会根据用户的问题，然后从知识库里提供相关答案，并且会将知识库里的英文新闻以中文的方式告诉用户，然后告诉他们想要的答案，不回答知识库没有赋予的答案的问题，
找不到的话不会跟用户废话，只需要强调自己还不够聪明不会回答这些问题。
问题: {question}
上下文: {context}
回答:
"""
prompt = PromptTemplate(template=template, input_variables=["question", "context"])

# 创建问答链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(temperature=0, base_url='https://api.chatanywhere.tech/v1/', api_key='sk-J5SBZ1hgnvUwJ4tfclSiET53pGaxP3m7mnIKfy3eoFXOGOEt'),
    chain_type="stuff",
    retriever=create_db(ack_knowledge).as_retriever(search_type="mmr",search_kwargs={'k': 10}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

generated_texts = []

def serialize_aimessagechunk(chunk):
    if isinstance(chunk,AIMessageChunk):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk.__name__)} is not a AIMessageChunk."
        )

async def rag_csv_bot_stream(query):
    async for event in qa_chain.astream_events({'query':query},version="v1"):
        if event["event"] == "on_chat_model_stream":
            chunk_content = serialize_aimessagechunk(event["data"]["chunk"])
            generated_texts.append(chunk_content)
            yield f"{chunk_content}"
        elif event["event"] == "on_chat_model_end":
            print("Chat model has completed its response.")

