# test_semantic_classifier.py
from processing.semantic_classifier import classify_style


def test_classify_pop_art():
    query = "Quiero algo tipo Andy Warhol, colores vibrantes y saturados"
    result = classify_style(query)
    assert result == "pop_art"


def test_classify_tenebrismo():
    query = "Retrato estilo Caravaggio con alto contraste y sombras"
    result = classify_style(query)
    assert result == "tenebrismo"


def test_classify_minimalismo():
    query = "Quiero un estilo limpio, desaturado y neutral"
    result = classify_style(query)
    assert result == "minimalismo"
