# prompt_builder.py


def build_prompt(user_query: str, filtered_metadata: dict) -> str:
    filters_descriptions = []
    for name, metadata in filtered_metadata.items():
        param_lines = []
        for param_name, param in metadata.get("params", {}).items():
            param_lines.append(
                f"{param_name}: {param['label']} ({param['type']}, default={param['default']}, range={param['range']})"
            )
        param_text = (
            "\n    " + "\n    ".join(param_lines)
            if param_lines
            else "    Sin parámetros configurables"
        )
        filters_descriptions.append(
            f"{name}:\n  Descripción: {metadata['description']}\n  Parámetros:{param_text}"
        )

    filters_block = "\n\n".join(filters_descriptions)

    prompt = f"""
Tu tarea es generar un JSON que contenga los filtros adecuados a partir de la siguiente petición del usuario.

Reglas:
- Usa solo los nombres de filtros disponibles.
- La salida debe tener este formato:

{{
  "filters_identified": [
    {{ "name": "apply_gaussian_blur", "ksize": 9 }},
    {{ "name": "convert_to_grayscale" }}
  ]
}}

Filtros disponibles:
{filters_block}

Petición del usuario: {user_query}
"""

    return prompt.strip()
