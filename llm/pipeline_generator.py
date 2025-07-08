# llm/pipeline_generator.py

from typing import Optional, List, Dict, Any
from processing.semantic_classifier import classify_style
from processing.filters import FILTER_METADATA
from llm.prompt_builder import build_prompt
from llm.client import LLMClient
from llm.parser import parse_llm_response
from llm.utils import get_filtered_metadata
from processing.predefined_pipelines import get_pipeline_from_rules
# from processing.validation import validate_filter_params


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
        self.last_used_fallback = False
        self.last_fallback_style = None

    def generate(self, user_query: str) -> Optional[List[Dict[str, Any]]]:
        self.last_used_fallback = False
        self.last_fallback_style = None

        # 1. Reglas predefinidas
        rule_based = get_pipeline_from_rules(user_query)
        if rule_based:
            print("[PipelineGenerator] 🎯 Pipeline obtenida desde reglas predefinidas.")
            self.last_used_fallback = True
            self.last_fallback_style = "regla_directa"
            return rule_based

        # 2. Clasificación semántica
        style = classify_style(user_query)
        print(f"[PipelineGenerator] Estilo detectado: {style}")

        # 3. Generación con LLM
        try:
            return self._generate_with_llm(user_query, style)
        except Exception as e:
            print(f"[PipelineGenerator] ❌ Error durante generación con LLM: {e}")
            return self._handle_fallback(style)

    def _generate_with_llm(
        self, user_query: str, style: str
    ) -> Optional[List[Dict[str, Any]]]:
        filtered_metadata = get_filtered_metadata(style, self.metadata)
        prompt = build_prompt(user_query, filtered_metadata)

        if self.debug:
            print("🧠 Prompt enviado al modelo:\n", prompt)

        response = self.llm.chat(
            system_prompt=prompt,
            user_input=user_query,
            temperature=self.temperature,
            max_tokens=1024,
        )

        if self.debug:
            print("📥 Respuesta cruda del modelo:\n", response)

        parsed = parse_llm_response(response, filtered_metadata)

        if parsed is None:
            raise ValueError("Respuesta no válida del modelo.")

        return parsed

    def _handle_fallback(self, style: str) -> List[Dict[str, Any]]:
        print("[PipelineGenerator] ⚠️ Fallback activado.")
        self.last_used_fallback = True
        self.last_fallback_style = style
        return self._fallback_pipeline(style)

    def _fallback_pipeline(self, style: str) -> List[Dict[str, Any]]:
        fallback_map = {
            "minimalismo": [
                {"name": "convert_to_grayscale"},
                {"name": "apply_gaussian_blur", "kernel_size": 3},
            ],
            "retratos": [
                {"name": "bokeh_effect"},
                {"name": "adjust_saturation", "intensity": 40},
            ],
            "nocturno": [
                {"name": "non_local_means_denoising"},
                {"name": "adjust_brightness_contrast", "contrast": 25},
            ],
            "pop_art": [
                {"name": "adjust_saturation", "intensity": 80},
                {"name": "invert_colors"},
            ],
            "tenebrismo": [
                {"name": "adjust_brightness_contrast", "contrast": 50},
                {"name": "apply_laplacian_sharpen"},
            ],
            "general": [{"name": "convert_to_grayscale"}],
        }
        return fallback_map.get(style, [{"name": "convert_to_grayscale"}])
