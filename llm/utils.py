# llm/utils.py

from typing import Dict, Any


def get_filtered_metadata(
    style_detected: str, full_metadata: Dict[str, Any], verbose: bool = False
) -> Dict[str, Any]:
    """
    Filtra FILTER_METADATA según el estilo detectado, devolviendo solo los filtros relevantes.

    Args:
        style_detected (str): Estilo semántico detectado (e.g., 'pop_art', 'minimalismo').
        full_metadata (dict): Diccionario completo de filtros disponibles.
        verbose (bool): Si es True, imprime información de depuración.

    Returns:
        dict: Subconjunto de full_metadata con filtros relevantes al estilo.
    """
    if not full_metadata:
        raise ValueError("FILTER_METADATA está vacío o no fue cargado correctamente.")

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
    if not selected_filters:
        if verbose:
            print(
                f"[Utils] Estilo '{style_detected}' no tiene filtros definidos. Usando todos."
            )
        selected_filters = list(full_metadata.keys())

    filtered = {f: full_metadata[f] for f in selected_filters if f in full_metadata}

    if verbose:
        print(
            f"[Utils] Filtros seleccionados para estilo '{style_detected}': {list(filtered.keys())}"
        )

    return filtered
