import cv2
import numpy as np
from processing.filters import FILTER_METADATA, get_default_filter_params
from processing.validation import validate_filter_params

def generate_test_image():
    """Crea una imagen de prueba simple en color."""
    return np.full((256, 256, 3), (120, 180, 240), dtype=np.uint8)

def run_filter_tests():
    image = generate_test_image()
    failed_filters = []

    for name, meta in FILTER_METADATA.items():
        func = meta["function"]
        default_params = get_default_filter_params(name)
        validated_params = validate_filter_params(name, default_params)

        try:
            print(f"🧪 Probando filtro: {name} con parámetros: {validated_params}")
            result = func(image.copy(), **validated_params)
            assert isinstance(result, np.ndarray), "El resultado no es una imagen"
            assert result.dtype == np.uint8, "El resultado no es uint8"
            print(f"✅ {name} pasó la prueba.\n")
        except Exception as e:
            print(f"❌ Error en filtro {name}: {e}")
            failed_filters.append(name)

    if failed_filters:
        print("❌ Filtros con errores:", failed_filters)
    else:
        print("🎉 Todos los filtros pasaron correctamente.")

if __name__ == "__main__":
    run_filter_tests()

