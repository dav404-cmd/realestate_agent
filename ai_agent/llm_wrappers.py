import re
from bytez import Bytez
from dotenv import load_dotenv
import os

import requests
import json


load_dotenv()

_THINK_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL)

class BytezLLM:
    def __init__(self, model_name: str):
        key = os.getenv("BYTEZ_KEY")
        if not key:
            raise ValueError("BYTEZ_KEY not found in .env")
        self.sdk = Bytez(key)
        self.model = self.sdk.model(model_name)

    def invoke(self, system: str | None = None, user: str = "", history:list | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})

        response = self.model.run(messages)

        if response.output is None:
            raise RuntimeError(f"LLM returned no output: {response.error}")

        content = response.output.get("content", "")
        content = re.sub(_THINK_REGEX, "", content).strip()

        return content

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