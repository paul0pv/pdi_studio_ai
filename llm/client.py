# llm/client.py

from llama_cpp import Llama
from typing import Optional


class LLMClient:
    def __init__(self, model_path: str = "models/Phi-3-mini-4k-instruct-q4.gguf"):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=4,
            n_gpu_layers=20,
            use_mlock=True,
            verbose=False,
        )

    def chat(
        self,
        system_prompt: str,
        user_input: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"].strip()
