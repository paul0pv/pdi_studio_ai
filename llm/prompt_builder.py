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


def build_prompt(
    user_query: str,
    metadata: Dict[str, Any],
    max_filters: int = 25,
    verbose: bool = False,
) -> str:
    if not metadata:
        raise ValueError("FILTER_METADATA está vacío o no fue cargado correctamente.")

    filter_descriptions = []
    for i, (name, meta) in enumerate(metadata.items()):
        if i >= max_filters:
            break
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

⚠️ IMPORTANTE:
- Responde únicamente con un objeto JSON válido.
- No incluyas explicaciones, comentarios ni texto adicional.
- Usa solo los filtros listados a continuación.
- Si no estás seguro, responde con una lista vacía: {{"filters_identified": []}}

Filtros disponibles:
{filters_text}

Ejemplo de respuesta válida:
{{
  "filters_identified": [
    {{"name": "convert_to_grayscale"}},
    {{"name": "adjust_brightness_contrast", "contrast": 20}}
  ]
}}

{EXAMPLES.strip()}

Ahora responde a esta solicitud del usuario:
"{user_query}"
""".strip()

    if verbose:
        print("[PromptBuilder] Prompt generado:")
        print(system_prompt)

    return system_prompt
