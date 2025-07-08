# processing/semantic_classifier.py

from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple

# Model initialization
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"❌ Error al cargar el modelo de embeddings: {e}")
    model = None

# Dict of semantic keywords
STYLE_KEYWORDS: Dict[str, List[str]] = {
    "pop_art": ["colores vibrantes", "saturado", "comic", "neón", "contraste alto"],
    "tenebrismo": [
        "caravaggio",
        "sombras intensas",
        "luz dramática",
        "barroco",
        "contraste",
    ],
    "minimalismo": ["limpio", "gris", "desaturado", "neutro", "claridad"],
    "retratos": ["rostros", "piel", "detalle facial", "fondo desenfocado", "bokeh"],
    "nocturno": ["noche", "ruido", "brillo bajo", "fotografía nocturna", "desenfoque"],
    "general": [],  # Fallback
}


def classify_style(user_query: str) -> str:
    """
    Retorna el estilo más cercano semánticamente al prompt del usuario.
    """
    if not model:
        return "general"

    best_style, _ = classify_style_with_score(user_query)
    return best_style


def classify_style_with_score(user_query: str) -> Tuple[str, float]:
    """
    Retorna el estilo más cercano y su score de similitud.
    """
    if not model:
        return "general", 0.0

    user_embedding = model.encode(user_query, convert_to_tensor=True)
    best_score = -1.0
    best_style = "general"

    for style, keywords in STYLE_KEYWORDS.items():
        if not keywords:
            continue
        style_text = " ".join(keywords)
        style_embedding = model.encode(style_text, convert_to_tensor=True)
        score = util.pytorch_cos_sim(user_embedding, style_embedding).item()
        if score > best_score:
            best_score = score
            best_style = style

    return best_style, best_score
