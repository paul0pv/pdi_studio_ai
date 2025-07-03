# semantic_classifier.py
from sentence_transformers import SentenceTransformer, util

# Inicialización del modelo
model = SentenceTransformer("all-MiniLM-L6-v2")

# Diccionario de estilos con palabras clave semánticas
STYLE_KEYWORDS = {
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

    return best_style
