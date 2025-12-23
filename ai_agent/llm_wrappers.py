import re
from bytez import Bytez
from dotenv import load_dotenv
import os

load_dotenv()

_THINK_REGEX = re.compile(r"<think>.*?</think>", re.DOTALL)

class BytezLLM:
    def __init__(self, model_name: str):
        key = os.getenv("BYTEZ_KEY")
        if not key:
            raise ValueError("BYTEZ_KEY not found in .env")
        self.sdk = Bytez(key)
        self.model = self.sdk.model(model_name)

    def invoke(self, system: str | None = None, user: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        response = self.model.run(messages)

        if response.output is None:
            raise RuntimeError(f"LLM returned no output: {response.error}")

        content = response.output.get("content", "")
        content = re.sub(_THINK_REGEX, "", content).strip()

        return content

