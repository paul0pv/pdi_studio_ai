# pdi_studio_ai/processing/predefined_pipelines.py

from typing import List, Dict, Any, Optional, Tuple
import copy
import difflib

# Semantic aliases for redirecting variants to base keys
PIPELINE_ALIASES = {
    "sepia": "tono sepia",
    "comic": "efecto comic",
    "pop art": "arte pop",
    "arte pop": "arte pop",
    "blanco y negro suave": "blanco y negro desenfocado",
    "alto contraste": "alto contraste blanco y negro",
    "bordes": "deteccion de bordes",
    "contraste": "ajustar brillo y contraste",
    "mejorar contraste": "ecualizar histograma",
    "suavizado global": "suavizado global",
}

# predefined rules... lol
PREDEFINED_PIPELINES = {
    "blanco y negro": [
        {"name": "convert_to_grayscale", "params": {}},
    ],
    "desenfoque gaussiano": [
        {"name": "apply_gaussian_blur", "params": {"ksize": 9}},
    ],
    "invertir colores": [
        {"name": "invert_colors", "params": {}},
    ],
    "tono sepia": [
        {"name": "sepia_tint", "params": {}},
    ],
    "nitido": [
        {"name": "apply_laplacian_sharpen", "params": {}},
    ],
    "blanco y negro desenfocado": [
        {"name": "convert_to_grayscale", "params": {}},
        {"name": "apply_gaussian_blur", "params": {"ksize": 9}},
    ],
    "desenfoque medio": [
        {"name": "apply_median_blur", "params": {"ksize": 9}},
    ],
    "deteccion de bordes": [
        {
            "name": "apply_canny_edge_detection",
            "params": {"low_threshold": 50, "high_threshold": 150},
        },
    ],
    "ajustar brillo y contraste": [
        {"name": "adjust_brightness_contrast", "params": {"alpha": 1.0, "beta": 0}},
    ],
    "desaturar": [
        {"name": "adjust_saturation", "params": {"saturation_factor": 0.5}},
    ],
    "saturar": [
        {"name": "adjust_saturation", "params": {"saturation_factor": 1.5}},
    ],
    "efecto bokeh": [
        {
            "name": "bokeh_effect",
            "params": {"ksize": 15, "center_x": 0.5, "center_y": 0.5, "radius": 0.2},
        },
    ],
    "efecto comic": [
        {"name": "convert_to_grayscale", "params": {}},
        {
            "name": "apply_canny_edge_detection",
            "params": {"low_threshold": 50, "high_threshold": 150},
        },
        {"name": "adjust_brightness_contrast", "params": {"alpha": 1.5, "beta": 30}},
    ],
    "arte pop": [
        {"name": "adjust_saturation", "params": {"saturation_factor": 2.0}},
        {"name": "adjust_brightness_contrast", "params": {"alpha": 1.2, "beta": 10}},
    ],
    "ecualizar histograma": [
        {"name": "equalize_histogram", "params": {}},
    ],
    "bordes suaves": [
        {
            "name": "apply_sobel_edge_detection",
            "params": {"dx": 1, "dy": 1, "ksize": 3},
        },
        {"name": "apply_gaussian_blur", "params": {"ksize": 5}},
    ],
    "suavizado global": [
        {"name": "apply_lowpass_fft", "params": {"cutoff": 0.1}},
    ],
    "alto contraste blanco y negro": [
        {"name": "convert_to_grayscale", "params": {}},
        {"name": "adjust_brightness_contrast", "params": {"alpha": 1.5, "beta": 20}},
    ],
}


def get_pipeline_from_rules(query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Devuelve un pipeline predefinido si el prompt coincide con una regla o alias.
    """
    normalized_query = query.strip().lower()
    resolved_key = PIPELINE_ALIASES.get(normalized_query, normalized_query)
    pipeline = PREDEFINED_PIPELINES.get(resolved_key)
    if pipeline:
        return copy.deepcopy(pipeline)
    return None


def suggest_closest_pipeline(
    query: str, cutoff: float = 0.6
) -> Optional[Tuple[str, List[Dict[str, Any]]]]:
    """
    Sugiere la regla más cercana si no hay coincidencia exacta.
    Retorna una tupla (nombre de la regla sugerida, pipeline) o None si no hay coincidencias razonables.
    """
    normalized_query = query.strip().lower()
    candidates = list(PREDEFINED_PIPELINES.keys()) + list(PIPELINE_ALIASES.keys())
    matches = difflib.get_close_matches(
        normalized_query, candidates, n=1, cutoff=cutoff
    )
    if matches:
        suggestion = matches[0]
        resolved_key = PIPELINE_ALIASES.get(suggestion, suggestion)
        pipeline = PREDEFINED_PIPELINES.get(resolved_key)
        if pipeline:
            return resolved_key, copy.deepcopy(pipeline)
    return None
