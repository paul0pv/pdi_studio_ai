# config/preset_meta.py

import json
import os
from typing import List, Dict

META_FILE = "config/preset_meta.json"


def _load_meta() -> dict:
    if not os.path.exists(META_FILE):
        return {"recent": [], "favorites": [], "tags": {}}
    try:
        with open(META_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"recent": [], "favorites": [], "tags": {}}


def _save_meta(meta: dict):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=4, ensure_ascii=False)


# 🕘 Recientes


def add_to_recent(preset_name: str):
    meta = _load_meta()
    recent = meta.get("recent", [])
    if preset_name in recent:
        recent.remove(preset_name)
    recent.insert(0, preset_name)
    meta["recent"] = recent[:10]
    _save_meta(meta)


def get_recent() -> List[str]:
    return _load_meta().get("recent", [])


# ⭐ Favoritos


def toggle_favorite(preset_name: str):
    meta = _load_meta()
    favs = meta.get("favorites", [])
    if preset_name in favs:
        favs.remove(preset_name)
    else:
        favs.append(preset_name)
    meta["favorites"] = favs
    _save_meta(meta)


def add_favorite(preset_name: str):
    meta = _load_meta()
    favs = meta.get("favorites", [])
    if preset_name not in favs:
        favs.append(preset_name)
        meta["favorites"] = favs
        _save_meta(meta)


def remove_favorite(preset_name: str):
    meta = _load_meta()
    favs = meta.get("favorites", [])
    if preset_name in favs:
        favs.remove(preset_name)
        meta["favorites"] = favs
        _save_meta(meta)


def get_favorites() -> List[str]:
    return _load_meta().get("favorites", [])


def is_favorite(preset_name: str) -> bool:
    return preset_name in get_favorites()


# 🏷️ Etiquetas


def tag_preset(preset_name: str, tag: str):
    meta = _load_meta()
    tags = meta.setdefault("tags", {})
    tags.setdefault(tag, [])
    if preset_name not in tags[tag]:
        tags[tag].append(preset_name)
    _save_meta(meta)


def untag_preset(preset_name: str, tag: str):
    meta = _load_meta()
    tags = meta.get("tags", {})
    if tag in tags and preset_name in tags[tag]:
        tags[tag].remove(preset_name)
        if not tags[tag]:
            del tags[tag]
    _save_meta(meta)


def get_presets_by_tag(tag: str) -> List[str]:
    return _load_meta().get("tags", {}).get(tag, [])


def get_tags_for_preset(preset_name: str) -> List[str]:
    meta = _load_meta()
    tags = meta.get("tags", {})
    return [t for t, presets in tags.items() if preset_name in presets]


def get_all_tags() -> List[str]:
    return list(_load_meta().get("tags", {}).keys())


def get_preset_tags() -> Dict[str, List[str]]:
    """
    Devuelve un diccionario con los nombres de los presets y sus etiquetas asociadas.
    """
    meta = _load_meta()
    tags = meta.get("tags", {})
    result = {}
    for tag, presets in tags.items():
        for p in presets:
            result.setdefault(p, []).append(tag)
    return result


def rename_preset_tag(old_name: str, new_name: str):
    """
    Actualiza las etiquetas asociadas a un preset cuando se renombra.
    """
    meta = _load_meta()
    tags = meta.get("tags", {})
    for tag, presets in tags.items():
        if old_name in presets:
            presets.remove(old_name)
            if new_name not in presets:
                presets.append(new_name)
    _save_meta(meta)
