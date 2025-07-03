# pipeline_generator.py

import json
from typing import Dict, Any, Optional, List
from processing.semantic_classifier import classify_style
from processing.filters import FILTER_METADATA
from llm.prompt_builder import build_prompt
from llm.llm_integrator import LLMIntegrator


def get_filtered_metadata(
    style_detected: str, full_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    style_to_filters = {
        "pop_art": ["adjust_saturation", "adjust_brightness_contrast", "invert_colors"],
        "tenebrismo": ["adjust_brightness_contrast", "apply_laplacian_sharpen"],
        "minimalismo": [
            "convert_to_grayscale",
            "apply_gaussian_blur",
            "non_local_means_denoising",
        ],
        "retratos": ["bokeh_effect", "adjust_saturation", "sepia_tint"],
        "nocturno": ["non_local_means_denoising", "adjust_brightness_contrast"],
        "general": list(full_metadata.keys()),
    }
    selected_filters = style_to_filters.get(style_detected, [])
    return {f: full_metadata[f] for f in selected_filters if f in full_metadata}


def generate_pipeline(user_query: str) -> Optional[List[Dict[str, Any]]]:
    # 1. Detectar estilo del input
    detected_style = classify_style(user_query)
    print(f"[Pipeline Generator] Estilo detectado: '{detected_style}'")

    # 2. Filtrar metadata relevante
    subset_metadata = get_filtered_metadata(detected_style, FILTER_METADATA)

    # 3. Construir prompt para el modelo
    prompt = build_prompt(user_query, subset_metadata)

    # 4. Ejecutar LLM
    integrator = LLMIntegrator()
    raw_response = integrator.llm.create_chat_completion(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query},
        ],
        temperature=0.2,
        max_tokens=2048,
    )

    try:
        raw_content = raw_response["choices"][0]["message"]["content"].strip()

        # Limpieza si viene con bloques ```json
        if raw_content.startswith("```json") and raw_content.endswith("```"):
            raw_content = raw_content[7:-3].strip()
        elif raw_content.startswith("```") and raw_content.endswith("```"):
            raw_content = raw_content[3:-3].strip()

        parsed_json = json.loads(raw_content)
        filters_list = parsed_json.get("filters_identified")

        # Validación básica de formato
        if not isinstance(filters_list, list):
            print("[Pipeline Generator] JSON inválido o incompleto.")
            return None

        # Validación detallada de cada filtro
        final_pipeline = []
        for item in filters_list:
            if not isinstance(item, dict) or "name" not in item:
                continue
            name = item["name"]
            if name not in FILTER_METADATA:
                continue

            metadata_params = FILTER_METADATA[name].get("params", {})
            valid_params = {}
            for param_key, param_value in item.items():
                if param_key == "name":
                    continue
                expected_type = metadata_params.get(param_key, {}).get("type")
                try:
                    if expected_type == "int_slider":
                        valid_params[param_key] = int(param_value)
                    elif expected_type == "float_slider":
                        valid_params[param_key] = float(param_value)
                    else:
                        valid_params[param_key] = param_value
                except Exception:
                    continue

            final_pipeline.append({"name": name, "params": valid_params})

        print(f"[Pipeline Generator] Pipeline generado: {final_pipeline}")
        return final_pipeline if final_pipeline else None

    except Exception as e:
        print(f"[Pipeline Generator] Error procesando la respuesta del LLM: {e}")
        return None
