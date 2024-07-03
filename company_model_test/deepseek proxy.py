from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uvicorn

# class Color:
#     def __init__(self, name, hex_value, rgb_value):
#         self.name = name
#         self.hex_value = hex_value
#         self.rgb_value = rgb_value

#     def __repr__(self):
#         return f"{self.name} (Hex: {self.hex_value}, RGB: {self.rgb_value})"
class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

    @staticmethod
    def colored_text(text, color):
        return f"{color}{text}{Color.RESET}"

class DeepSeekAPI:
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    DEEPSEEK_API_KEY = "sk-ab273b67e6e64f399870cf37b33cf34f"

    @classmethod
    def send_request(cls, request_data):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cls.DEEPSEEK_API_KEY}"
        }
        try:
            response = requests.post(cls.DEEPSEEK_API_URL, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request to DeepSeek API failed: {e}")
            raise HTTPException(status_code=response.status_code, detail=f"Error contacting DeepSeek API: {e}")
        except ValueError:
            print(f"Invalid JSON response received from DeepSeek API: {response.text}")
            raise HTTPException(status_code=500, detail="Invalid JSON response received from DeepSeek API")

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

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    original_model = request.model
    request.model = "deepseek-chat"
    # print(f"Request Data: {Color('Green', '#00FF00', (0, 255, 0))} {request.dict()}\n")
    print(Color.colored_text(f"Request Data: {request.dict()}\n", Color.GREEN))
    response_json = DeepSeekAPI.send_request(request.dict())
    # print(f"Response Data: {Color('Blue', '#0000FF', (0, 0, 255))} {response_json}\n")
    print(Color.colored_text(f"Response Data: {response_json}\n", Color.BLUE))
    openai_response = ResponseTransformer.transform(response_json, original_model)
    # print(f"Response Data: {Color('Blue', '#FF0000', (255, 0, 0))} {openai_response}\n")
    print(Color.colored_text(f"Transformed Response Data: {openai_response}\n", Color.RED))

    return openai_response

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=1511)