import requests
import json

class BaseModel:
    def request(self,question):
        raise NotImplementedError

class OPENAI(BaseModel):
    header =  {'Content-Type': 'application/json', 'api-key': 'c739981ee79541deb8414f0bd8bb576c'}

    def __init__(self):
        self.url = 'https://tcl-azure-westus3.openai.azure.com/openai/deployments/tcl-gpt4o1/chat/completions?api-version=2024-04-01-preview'

    def gpt_4o_request(self, prompt,query):
        data = {
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {
                    "type": "text",
                    "text": query,
                }
                ]}
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "top_p": 0.95,
            "stop": None,
        }
        response = requests.post(self.url, data=json.dumps(data), headers=self.header, timeout = 300)
        all_result = json.loads(response.text)
        slots = all_result["choices"][0]["message"]["content"]
        return slots