# llm/parser.py

import json
from typing import List, Dict, Any, Optional


def parse_llm_response(
    raw_response: str, metadata: Dict[str, Any]
) -> Optional[List[Dict[str, Any]]]:
    try:
        # Limpieza si viene con bloques ```json
        if raw_response.startswith("```json") and raw_response.endswith("```"):
            raw_response = raw_response[7:-3].strip()
        elif raw_response.startswith("```") and raw_response.endswith("```"):
            raw_response = raw_response[3:-3].strip()

        parsed_json = json.loads(raw_response)
        filters_list = parsed_json.get("filters_identified")

        if not isinstance(filters_list, list):
            print("[Parser] JSON inválido o incompleto.")
            return None

        final_pipeline = []
        for item in filters_list:
            if not isinstance(item, dict) or "name" not in item:
                continue
            name = item["name"]
            if name not in metadata:
                continue

            metadata_params = metadata[name].get("params", {})
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

        return final_pipeline if final_pipeline else None

    except Exception as e:
        print(f"[Parser] Error procesando la respuesta del LLM: {e}")
        return None
