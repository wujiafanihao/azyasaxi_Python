from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate,SystemMessagePromptTemplate,HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

def get_document_basedon_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pdf = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=100,chunk_overlap=10)
    splitterPdf = splitter.split_documents(pdf)
    return splitterPdf
pdf = get_document_basedon_pdf("langchain.pdf")
def create_db(pdf):
    embeddings=OllamaEmbeddings(model="nomic-embed-text")
    vectorStore = Chroma.from_documents(
        pdf,embedding=embeddings
    )
    return vectorStore

if __name__ == "__main__":
    retriever = create_db(pdf).as_retriever()
    template = "{context}"
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(template),
        HumanMessagePromptTemplate.from_template("{quetion}")
    ])
    llm = ChatOpenAI(temperature=0)
    retriever_chain = (
            {"context": retriever, "quetion": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    response = retriever_chain.stream({
        "quetion":"What is langchain?",
    })
    for chunk in response:
        print(chunk,end="",flush=True)