# conftest.py
import pytest
from processing.filters import FILTER_METADATA


@pytest.fixture
def sample_queries():
    return {
        "pop_art": "Quiero colores vibrantes, estilo cómic y mucha saturación",
        "tenebrismo": "Retrato tipo Caravaggio con sombras profundas y alto contraste",
        "minimalismo": "Estética neutra y limpia, sin saturación",
        "retratos": "Imagen tipo retrato, fondo desenfocado y tono cálido",
        "nocturno": "Fotografía nocturna con reducción de ruido y bajo brillo",
    }


@pytest.fixture
def full_metadata():
    return FILTER_METADATA
