# llm/parser.py

import json
from typing import List, Dict, Any, Optional
from processing.validation import validate_filter_params


def parse_llm_response(
    raw_response: str, metadata: Dict[str, Any], verbose: bool = True
) -> Optional[List[Dict[str, Any]]]:
    """
    Parsea la respuesta JSON generada por el LLM y la convierte en un pipeline válido.
    """
    try:
        # Limpieza de delimitadores Markdown
        if raw_response.startswith("```json") and raw_response.endswith("```"):
            raw_response = raw_response[7:-3].strip()
        elif raw_response.startswith("```") and raw_response.endswith("```"):
            raw_response = raw_response[3:-3].strip()

        if not raw_response.strip():
            if verbose:
                print("[Parser] Respuesta vacía del modelo.")
            return None

        if not raw_response.strip().startswith("{"):
            if verbose:
                print("[Parser] Respuesta no parece ser JSON.")
                print("Contenido recibido:", raw_response)
            return None

        parsed_json = json.loads(raw_response)
        filters_list = parsed_json.get("filters_identified")

        if not isinstance(filters_list, list):
            if verbose:
                print("[Parser] JSON inválido o campo 'filters_identified' ausente.")
            return None

        final_pipeline = []
        for item in filters_list:
            if not isinstance(item, dict) or "name" not in item:
                if verbose:
                    print(f"[Parser] Entrada inválida: {item}")
                continue

            name = item["name"]
            if name not in metadata:
                if verbose:
                    print(f"[Parser] Filtro '{name}' no reconocido. Omitido.")
                continue

            valid_params = validate_filter_params(name, item)
            final_pipeline.append({"name": name, "params": valid_params})

        if not final_pipeline:
            if verbose:
                print("[Parser] No se extrajo ningún filtro válido.")
            return None

        return final_pipeline

    except json.JSONDecodeError as e:
        if verbose:
            print(f"[Parser] Error de decodificación JSON: {e}")
        return None
    except Exception as e:
        if verbose:
            print(f"[Parser] Error inesperado: {e}")
        return None
