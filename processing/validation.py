from processing.filters import FILTER_METADATA


def clamp_value(value, min_val, max_val):
    return max(min_val, min(value, max_val))


def validate_filter_params(filter_name: str, params: dict) -> dict:
    """
    Valida y corrige los parámetros de un filtro según su metadata.
    Retorna un nuevo diccionario con los valores corregidos.
    """
    metadata = FILTER_METADATA.get(filter_name, {})
    param_defs = metadata.get("params", {})
    validated = {}

    for param_name, param_info in param_defs.items():
        default = param_info.get("default")
        min_val, max_val, _ = param_info.get("range", (None, None, None))
        value = params.get(param_name, default)

        if isinstance(value, (int, float)) and min_val is not None and max_val is not None:
            value = clamp_value(value, min_val, max_val)

        validated[param_name] = value

    return validated

