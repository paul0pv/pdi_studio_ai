# pdi_studio_ai/processing/predefined_pipelines.py

from typing import List, Dict, Any, Optional
import copy

# Define pre-configured pipelines for common natural language requests.
# Keys are user query phrases (lowercase, stripped) and values are
# lists of filter configurations, matching the structure expected by ImageProcessor.
# Ensure 'params' is an empty dict {} if no parameters are needed for a filter.
PREDEFINED_PIPELINES = {
    "blanco y negro": [
        {"name": "convert_to_grayscale", "params": {}},
    ],
    "desenfoque gaussiano": [
        {"name": "apply_gaussian_blur", "params": {"ksize": 9}},  # ksize default
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
        {
            "name": "apply_median_blur",
            "params": {"ksize": 9},
        },  # ksize default for median
    ],
    "deteccion de bordes": [
        {
            "name": "apply_canny_edge_detection",
            "params": {"low_threshold": 50, "high_threshold": 150},
        },
    ],
    "ajustar brillo y contraste": [
        {
            "name": "adjust_brightness_contrast",
            "params": {"alpha": 1.0, "beta": 0},
        },  # Default no change
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
        },  # Example defaults
    ],
    # Ejemplos de efectos más "artísticos" predefinidos:
    # Estos son complejos y a menudo requieren una combinación de filtros.
    # Si el LLM falla, podrían añadirse aquí si se puede definir una secuencia fija.
    "efecto comic": [
        {"name": "convert_to_grayscale", "params": {}},
        {
            "name": "apply_canny_edge_detection",
            "params": {"low_threshold": 50, "high_threshold": 150},
        },
        {
            "name": "adjust_brightness_contrast",
            "params": {"alpha": 1.5, "beta": 30},
        },  # Aumenta contraste
        # Nota: El efecto cómic real a menudo implica posterización y colores planos,
        # que no tenemos como filtros directos todavía. Esto es una aproximación.
    ],
    "arte pop": [
        {
            "name": "adjust_saturation",
            "params": {"saturation_factor": 2.0},
        },  # Colores muy vivos
        {
            "name": "adjust_brightness_contrast",
            "params": {"alpha": 1.2, "beta": 10},
        },  # Contraste alto
        # Nuevamente, la posterización/cuantificación de color sería ideal aquí.
    ],
    # Añade más reglas aquí según identifiques peticiones comunes de los usuarios.
    # Puedes añadir variaciones como "desenfoque fuerte" -> {"ksize": 25}
    # o "blanco y negro con alto contraste" -> [grayscale, adjust_brightness_contrast(alpha=1.5)]
}


def get_pipeline_from_rules(query: str) -> Optional[List[Dict[str, Any]]]:
    """
    Checks if a user query (case-insensitive, trimmed) matches a predefined rule
    and returns a deep copy of the corresponding pipeline configuration.
    Returns None if no rule matches.
    """
    normalized_query = query.strip().lower()
    pipeline = PREDEFINED_PIPELINES.get(normalized_query)
    if pipeline:
        # Return a deep copy to prevent external modifications to the original PREDEFINED_PIPELINES
        return copy.deepcopy(pipeline)
    return None
