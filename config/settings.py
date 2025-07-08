import json
import os


class SettingsManager:
    DEFAULTS = {
        "llm_enabled": False,
        "suppress_llm_prompt": False,
        # Futuras extensiones:
        # "preferred_model": "phi-3-mini",
        # "language": "es",
        # "theme": "dark"
    }

    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.settings = {}
        self._ensure_config_directory()
        self.load()

    def _ensure_config_directory(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def load(self):
        """Carga la configuración desde disco, aplicando valores por defecto si es necesario."""
        if not os.path.exists(self.config_path):
            self.settings = self.DEFAULTS.copy()
            self.save()
        else:
            try:
                with open(self.config_path, "r") as f:
                    self.settings = json.load(f)
                self._ensure_keys()
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error al cargar configuración: {e}")
                self.settings = self.DEFAULTS.copy()
                self.save()

    def _ensure_keys(self):
        """Asegura que todas las claves mínimas estén presentes."""
        for key, value in self.DEFAULTS.items():
            self.settings.setdefault(key, value)

    def save(self):
        """Guarda la configuración actual en disco."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"❌ Error al guardar configuración: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def all(self):
        """Devuelve el diccionario completo de configuración."""
        return self.settings
