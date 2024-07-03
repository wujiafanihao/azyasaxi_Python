from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
from langchain.chains import ConversationChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
import asyncio
import sys

def track_tokens_usage(chain,query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f"Total tokens:{cb.total_tokens}")

    return result

load_dotenv()

# memory = ConversationBufferMemory(memory_key="chat_history")

handler = AsyncIteratorCallbackHandler()
llm = ChatOpenAI(
    streaming=True, 
    callbacks=[handler], 
    temperature=0,
    verbose=True,
)

conversation = ConversationChain(llm=llm, memory=ConversationBufferMemory()) 
print(conversation.prompt.template)
track_tokens_usage(conversation,"What is Langchain?")

async def consumer():
    iterator = handler.aiter()
    async for item in iterator:
        sys.stdout.write(item)
        sys.stdout.flush()

if __name__ == '__main__':
    message = "What is Langchain"
    loop = asyncio.get_event_loop()
    loop.create_task(llm.agenerate(messages=[[HumanMessage(content=message)]]))
    loop.create_task(consumer())
    loop.run_forever()
    loop.close()