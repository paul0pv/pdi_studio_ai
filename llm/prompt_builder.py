# llm/prompt_builder.py

from typing import Dict, Any

EXAMPLES = """
Ejemplo 1:
Usuario: Quiero un estilo pop art con colores saturados y bordes definidos.
Respuesta:
{
  "filters_identified": [
    {"name": "adjust_saturation", "intensity": 80},
    {"name": "adjust_brightness_contrast", "contrast": 30},
    {"name": "invert_colors"}
  ]
}

Ejemplo 2:
Usuario: Me gustaría una imagen suave y minimalista en blanco y negro.
Respuesta:
{
  "filters_identified": [
    {"name": "convert_to_grayscale"},
    {"name": "apply_gaussian_blur", "kernel_size": 5}
  ]
}
"""


def build_prompt(user_query: str, metadata: Dict[str, Any]) -> str:
    filter_descriptions = []
    for name, meta in metadata.items():
        desc = meta.get("description", "")
        params = meta.get("params", {})
        param_str = ", ".join(
            f"{k} ({v.get('type', 'valor')})" for k, v in params.items()
        )
        if param_str:
            filter_descriptions.append(f"- {name}: {desc}. Parámetros: {param_str}")
        else:
            filter_descriptions.append(f"- {name}: {desc}.")

    filters_text = "\n".join(filter_descriptions)

    system_prompt = f"""
Eres un asistente experto en procesamiento de imágenes. Tu tarea es analizar una descripción en lenguaje natural y devolver una lista de filtros de imagen que se deben aplicar, en formato JSON.

Solo debes usar los filtros disponibles que se listan a continuación. Cada filtro puede tener parámetros opcionales. Si no se especifican, usa valores por defecto razonables.

Filtros disponibles:
{filters_text}

Formato de respuesta esperado:
{EXAMPLES}

Ahora responde a la siguiente solicitud del usuario:
"""

    return system_prompt.strip()
