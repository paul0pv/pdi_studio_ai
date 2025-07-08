# ui/widgets/favorites_tab.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QHBoxLayout,
)
from config.presets import load_presets
from config.preset_meta import (
    get_favorites,
    get_all_tags,
    get_presets_by_tag,
    is_favorite,
    add_favorite,
    remove_favorite,
)


class FavoritesTab(QWidget):
    def __init__(self, on_apply_callback):
        super().__init__()
        self.presets = load_presets()
        self.on_apply_callback = on_apply_callback

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)

        self.label = QLabel("⭐ Favoritos:")
        self.combo = QComboBox()
        self.combo.currentTextChanged.connect(self._update_preview)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self._apply_selected)

        self.favorite_toggle = QPushButton("★ Alternar favorito")
        self.favorite_toggle.clicked.connect(self._toggle_favorite)

        self.filter_label = QLabel("🏷️ Filtrar por etiqueta:")
        self.tag_combo = QComboBox()
        self.tag_combo.currentTextChanged.connect(self._filter_by_tag)

        # Layouts
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.preview)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.apply_button)
        btn_row.addWidget(self.favorite_toggle)
        self.layout.addLayout(btn_row)

        self.layout.addWidget(self.filter_label)
        self.layout.addWidget(self.tag_combo)

    def refresh(self):
        self.presets = load_presets()
        self._refresh_tag_combo()
        self._refresh_combo(get_favorites())

    def _refresh_tag_combo(self):
        from config.preset_meta import get_all_tags

        self.tag_combo.blockSignals(True)
        self.tag_combo.clear()
        self.tag_combo.addItem("Todos")
        self.tag_combo.addItems(sorted(get_all_tags()))
        self.tag_combo.blockSignals(False)

    def _refresh_combo(self, preset_names):
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItems(sorted(preset_names))
        self.combo.blockSignals(False)
        if self.combo.count() > 0:
            self._update_preview(self.combo.currentText())
        else:
            self.preview.setText("⚠️ No hay presets disponibles para esta etiqueta.")

    def _update_preview(self, name: str):
        pipeline = self.presets.get(name, [])
        if not pipeline:
            self.preview.setText("⚠️ Este preset está vacío.")
            return

        lines = []
        for f in pipeline:
            fname = f.get("name", "¿?")
            params = f.get("params", {})
            lines.append(f"🔧 {fname} → {params}")
        self.preview.setText("\n".join(lines))

    def _apply_selected(self):
        name = self.combo.currentText()
        pipeline = self.presets.get(name)
        if pipeline:
            self.on_apply_callback(name, pipeline)
        else:
            QMessageBox.warning(
                self, "Error", "No se pudo aplicar el preset seleccionado."
            )

    def _filter_by_tag(self, tag: str):
        if tag == "Todos":
            self._refresh_combo(get_favorites())
        else:
            tagged = get_presets_by_tag(tag)
            filtered = [p for p in tagged if is_favorite(p)]
            self._refresh_combo(filtered)

    def _toggle_favorite(self):
        name = self.combo.currentText()
        if not name:
            return
        if is_favorite(name):
            remove_favorite(name)
            QMessageBox.information(
                self, "Favorito", f"Preset '{name}' eliminado de favoritos."
            )
        else:
            add_favorite(name)
            QMessageBox.information(
                self, "Favorito", f"Preset '{name}' marcado como favorito."
            )
        self.refresh()
