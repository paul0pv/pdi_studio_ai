from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QTextEdit,
)
from config.presets import load_presets
from config.preset_meta import get_favorites, get_all_tags, get_presets_by_tag


class FavoritesTab(QWidget):
    def __init__(self, on_apply_callback):
        super().__init__()
        self.presets = load_presets()
        self.on_apply_callback = on_apply_callback

        layout = QVBoxLayout()

        self.label = QLabel("⭐ Favoritos:")
        self.combo = QComboBox()
        self.combo.addItems(get_favorites())
        self.combo.currentTextChanged.connect(self._update_preview)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)

        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self._apply_selected)

        self.filter_label = QLabel("🏷️ Filtrar por etiqueta:")
        self.tag_combo = QComboBox()
        self.tag_combo.addItems([""] + get_all_tags())
        self.tag_combo.currentTextChanged.connect(self._filter_by_tag)

        layout.addWidget(self.label)
        layout.addWidget(self.combo)
        layout.addWidget(self.preview)
        layout.addWidget(self.apply_button)
        layout.addWidget(self.filter_label)
        layout.addWidget(self.tag_combo)

        self.setLayout(layout)
        if self.combo.count() > 0:
            self._update_preview(self.combo.currentText())

    def _update_preview(self, name: str):
        pipeline = self.presets.get(name, [])
        self.preview.setText(
            "\n".join([f"{f['name']} → {f.get('params', {})}" for f in pipeline])
        )

    def _apply_selected(self):
        name = self.combo.currentText()
        pipeline = self.presets.get(name)
        if pipeline:
            self.on_apply_callback(name, pipeline)

    def _filter_by_tag(self, tag: str):
        if not tag:
            self.combo.clear()
            self.combo.addItems(get_favorites())
        else:
            tagged = get_presets_by_tag(tag)
            self.combo.clear()
            self.combo.addItems(tagged)
