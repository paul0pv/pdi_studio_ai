# llm/pipeline_generator.py

from typing import Optional, List, Dict, Any
from processing.semantic_classifier import classify_style
from processing.filters import FILTER_METADATA
from llm.prompt_builder import build_prompt
from llm.client import LLMClient
from llm.parser import parse_llm_response
from llm.utils import get_filtered_metadata


class PipelineGenerator:
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        metadata: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        temperature: float = 0.2,
    ):
        self.llm = llm_client or LLMClient()
        self.metadata = metadata or FILTER_METADATA
        self.debug = debug
        self.temperature = temperature

    def generate(self, user_query: str) -> Optional[List[Dict[str, Any]]]:
        style = classify_style(user_query)
        print(f"[PipelineGenerator] Estilo detectado: {style}")

        filtered_metadata = get_filtered_metadata(style, self.metadata)
        prompt = build_prompt(user_query, filtered_metadata)

        if self.debug:
            print("🔍 Prompt generado:\n", prompt)
            print("🧠 User input:\n", user_query)

        response = self.llm.chat(
            system_prompt=prompt,
            user_input=user_query,
            temperature=self.temperature,
            max_tokens=2048,
        )

        return parse_llm_response(response, filtered_metadata)
