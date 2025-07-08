# processing/validation.py

from processing.filters import FILTER_METADATA


def clamp_value(value, min_val, max_val):
    """Restringe un valor dentro de un rango."""
    return max(min_val, min(value, max_val))


def ensure_odd(value: int) -> int:
    """Garantiza que un valor sea impar (para kernels)."""
    return value if value % 2 == 1 else value + 1


# 🔍 Extended validator by filters (optional)
EXTENDED_VALIDATORS = {
    "apply_sobel_edge_detection": lambda params: _validate_sobel_direction(params),
    # More validators here
}


def _validate_sobel_direction(params: dict) -> dict:
    """
    Valida que al menos una dirección (dx o dy) esté activa.
    Si ambas son cero, activa dx por defecto.
    """
    dx = params.get("dx", 0)
    dy = params.get("dy", 0)
    if dx == 0 and dy == 0:
        print("⚠️ Sobel: dx y dy no pueden ser ambos cero. Activando dx=1 por defecto.")
        params["dx"] = 1
    return params


def validate_filter_params(filter_name: str, params: dict) -> dict:
    """
    Valida y corrige parámetros según metadatos del filtro.
    Maneja rangos, tipos, imparidad y validación extendida.
    """
    metadata = FILTER_METADATA.get(filter_name, {})
    param_defs = metadata.get("params", {})
    validated = {}

    for param_name, param_info in param_defs.items():
        raw_value = params.get(param_name, param_info.get("default"))
        expected_type = param_info.get("type", "")
        value = raw_value

        # Type validation
        try:
            if expected_type == "int_slider":
                value = int(value)
            elif expected_type == "float_slider":
                value = float(value)
        except (ValueError, TypeError):
            print(
                f"⚠️ Parámetro inválido '{param_name}' en '{filter_name}', usando valor por defecto."
            )
            value = param_info.get("default")

        # Range validation
        if "range" in param_info:
            min_val, max_val, _ = param_info["range"]
            value = clamp_value(value, min_val, max_val)

        # Parity validation
        if param_info.get("must_be_odd", False):
            value = ensure_odd(value)

        validated[param_name] = value

    # Undefined parameters warning
    for key in params:
        if key not in param_defs:
            print(f"⚠️ Parámetro '{key}' no reconocido para el filtro '{filter_name}'.")

    # Extended validation if applies
    if filter_name in EXTENDED_VALIDATORS:
        validated = EXTENDED_VALIDATORS[filter_name](validated)

    return validated
