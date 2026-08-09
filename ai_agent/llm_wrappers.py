import re
from dotenv import load_dotenv
import os

import requests

load_dotenv()

_THINK_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL)

class OpenRouterLLM:
    def __init__(self,model_name:str):
        self.key = os.getenv("OPENROUTER_KEY")
        if not self.key:
            raise ValueError("OPENROUTER_KEY not found in .env")
        self.model = model_name

    def invoke(self,system:str | None = None , user: str = "",history:list | None = None) -> str:
        messages = []
        if system:
            messages.append({"role":"system","content":system})
        if history:
            messages.extend(history)
        messages.append({"role":"user","content":user})

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json = {
                "model": self.model,
                "messages": messages
            },
        timeout=30
        )
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError,IndexError):
            raise RuntimeError(f"Unexpected OpenRouter response: {data}")

class GloqLLM:
    def __init__(self,model_name:str):
        self.key = os.getenv("GLOQ_KEY")
        if not self.key:
            raise ValueError("GLOQ_KEY not found in .env")
        self.model = model_name

    def invoke(self,system:str | None = None,user:str = "",history : list | None = None) -> str:
        messages = []
        if system:
            messages.append({"role" : "system","content" : system})
        if history:
            messages.extend(history)
        messages.append({"role" : "user", "content" : user})

        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers = {
                "Authorization" : f"Bearer {self.key}",
                "Content-Type": "application/json",
            },
            json = {
                "model" : self.model,
                "messages" : messages
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected OpenRouter response: {data}")

if __name__ == "__main__":
    #--Test--
    agent = GloqLLM("openai/gpt-oss-120b")
    res=agent.invoke(user="hello")
    print(res)