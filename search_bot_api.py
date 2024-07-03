from fastapi import FastAPI
from search_bot import rag_csv_bot_stream
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["POST"],  
    allow_headers=["*"],
)

@app.post("/v1/chat/completions", response_class=StreamingResponse)
async def ask(body: dict):
    async def print_and_stream(query):
        async for response in rag_csv_bot_stream(query):
            print(response)  # 打印回复的值
            yield response

    return StreamingResponse(print_and_stream(body['query']), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run("search_bot_api:app", host="127.0.0.1", port=8088, reload=True, log_level="debug")