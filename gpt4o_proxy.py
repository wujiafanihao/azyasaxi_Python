import requests
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

class OPENAIAPI:
    OPENAI_BASE_URL = "https://tcl-azure-westus3.openai.azure.com/openai/deployments/tcl-gpt4o1/chat/completions?api-version=2024-04-01-preview"
    OPENAI_API_KEY = "c739981ee79541deb8414f0bd8bb576c"

    @classmethod
    def send_request(cls, request_data):
        headers = {
            "Content-Type": "application/json",
            "api-key": cls.OPENAI_API_KEY
        }
        try:
            print(f"Sending request to OPENAI API: {json.dumps(request_data, indent=2).encode('utf-8')}")
            response = requests.post(cls.OPENAI_BASE_URL, headers=headers, json=request_data)
            response.raise_for_status()
            print(f"Received response status: {response.status_code}")
            print(f"Received response text: {response.text}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request to OPENAI API failed: {e}")
            raise HTTPException(status_code=response.status_code if response else 500, detail=f"Error contacting OPENAI API: {e}")
        except ValueError as e:
            print(f"Invalid JSON response received from OPENAI API: {response.text}")
            raise HTTPException(status_code=500, detail=f"Invalid JSON response received from OPENAI API: {e}")

class ResponseTransformer:
    @staticmethod
    def transform(response_json, original_model):
        return {
            "id": response_json.get("id"),
            "object": "chat.completion",
            "created": response_json.get("created"),
            "model": original_model,
            "choices": [{
                "index": choice.get("index"),
                "message": {
                    "role": choice.get("message").get("role"),
                    "content": choice.get("message").get("content")
                },
                "finish_reason": choice.get("finish_reason"),
                "logprobs": choice.get("logprobs")
            } for choice in response_json.get("choices", [])],
            "usage": response_json.get("usage")
        }

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False

def generate_streaming_response(response_json):
    for choice in response_json['choices']:
        content = choice['message']['content']
        for i in range(0, len(content), 10):  # 每10个字符分割一次
            chunk = json.dumps({
                "id": response_json.get("id"),
                "object": "chat.completion.chunk",
                "created": response_json.get("created"),
                "model": response_json.get("model"),
                "choices": [{
                    "index": choice.get("index"),
                    "delta": {
                        "content": content[i:i+10]
                    }
                }],
                "finish_reason": None if i + 10 < len(content) else choice.get("finish_reason")
            })
            yield f"data: {chunk}\n\n"
    yield f"data: [DONE]\n\n"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    original_model = request.model
    request.model = "gpt-4o-2024-05-13"
    response_json = OPENAIAPI.send_request(request.dict())
    openai_response = ResponseTransformer.transform(response_json, original_model)
    
    if request.stream:
        return StreamingResponse(generate_streaming_response(response_json), media_type="text/event-stream")
    else:
        return openai_response

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
