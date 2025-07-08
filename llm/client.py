# llm/client.py

from llama_cpp import Llama
from typing import Optional, Dict


class LLMClient:
    def __init__(
        self,
        model_path: str = "models/Phi-3-mini-4k-instruct-q4.gguf",
        n_ctx: int = 4096,
        n_threads: int = 4,
        n_gpu_layers: int = 20,
        n_batch: int = 512,
        use_mlock: bool = True,
        verbose: bool = False,
        main_gpu: int = 0,
    ):
        self.model_path = model_path
        self.config = {
            "n_ctx": n_ctx,
            "n_threads": n_threads,
            "n_gpu_layers": n_gpu_layers,
            "n_batch": n_batch,
            "use_mlock": use_mlock,
            "verbose": verbose,
            "main_gpu": main_gpu,
        }
        self.llm = self._load_model()

    def _load_model(self) -> Optional[Llama]:
        try:
            print(f"[LLMClient] Cargando modelo desde: {self.model_path}")
            return Llama(model_path=self.model_path, **self.config)
        except Exception as e:
            print(f"[❌] Error al cargar el modelo LLM: {e}")
            return None

    def chat(
        self,
        system_prompt: str,
        user_input: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> str:
        if not self.llm:
            return "[ERROR] Modelo no cargado."

        try:
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[❌] Error durante inferencia LLM: {e}")
            return "[ERROR] Fallo en la generación de respuesta."

    def reload_model(self, new_model_path: str):
        """Permite recargar el modelo desde otro archivo."""
        self.model_path = new_model_path
        self.llm = self._load_model()
