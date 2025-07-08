# ui/widgets/filter_control.py

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QSpinBox,
    QSlider,
    QDoubleSpinBox,
    QGroupBox,
    QMenu,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from processing.filters import FILTER_METADATA
from processing.validation import validate_filter_params


class FilterControl(QGroupBox):
    params_changed = pyqtSignal(str, dict, int)
    enabled_toggled = pyqtSignal(str, bool, int)
    removed = pyqtSignal(int)
    moved = pyqtSignal(int, str)
    duplicated = pyqtSignal(int)

    def __init__(self, filter_name: str, initial_params: dict, index: int):
        super().__init__(filter_name)
        self.filter_name = filter_name
        self.current_params = initial_params
        self._index = index
        self.filter_metadata = FILTER_METADATA.get(filter_name, {})
        self.setStyleSheet("QGroupBox { font-weight: bold; }")

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.enabled_checkbox = QCheckBox("Activado")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.stateChanged.connect(self._on_enabled_toggled)
        self.layout.addWidget(self.enabled_checkbox)

        self.param_widgets = {}
        self._build_param_controls()

        # Botones de acción
        btn_layout = QHBoxLayout()
        self.remove_btn = QPushButton("Eliminar")
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self._index))
        self.up_btn = QPushButton("↑")
        self.up_btn.clicked.connect(lambda: self.moved.emit(self._index, "up"))
        self.down_btn = QPushButton("↓")
        self.down_btn.clicked.connect(lambda: self.moved.emit(self._index, "down"))
        self.duplicate_btn = QPushButton("Duplicar")
        self.duplicate_btn.clicked.connect(lambda: self.duplicated.emit(self._index))

        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        btn_layout.addWidget(self.duplicate_btn)
        btn_layout.addWidget(self.remove_btn)
        self.layout.addLayout(btn_layout)

    def _build_param_controls(self):
        def create_spinbox(param_type, min_val, max_val, step, default):
            if param_type == "float_slider":
                sb = QDoubleSpinBox()
                sb.setDecimals(3)
                sb.setSingleStep(float(step))
                sb.setValue(float(default))
            else:
                sb = QSpinBox()
                sb.setSingleStep(int(step))
                sb.setValue(int(default))
            sb.setMinimum(min_val)
            sb.setMaximum(max_val)
            return sb

        def highlight_if_invalid(widget, is_valid: bool):
            palette = widget.palette()
            if not is_valid:
                palette.setColor(
                    QPalette.ColorRole.Base, QColor("#ffcccc")
                )  # rojo claro
            else:
                palette.setColor(QPalette.ColorRole.Base, QColor("white"))
            widget.setPalette(palette)

        for param_name, param_info in self.filter_metadata.get("params", {}).items():
            param_type = param_info.get("type", "int_slider")
            default = self.current_params.get(param_name, param_info.get("default", 0))
            range_vals = param_info.get("range", (0, 100))

            if not isinstance(range_vals, (list, tuple)) or len(range_vals) < 2:
                print(f"[⚠️] Rango inválido para parámetro: {range_vals}")
                range_vals = (0, 100)

            min_val = range_vals[0]
            max_val = range_vals[1]
            step = range_vals[2] if len(range_vals) > 2 else 1
            must_be_odd = param_info.get("must_be_odd", False)

            row = QHBoxLayout()
            label = QLabel(param_info.get("label", param_name))
            label.setToolTip(param_info.get("description", ""))
            row.addWidget(label)

            if param_type in ("int_slider", "float_slider"):
                scale = int(1 / step) if param_type == "float_slider" else 1

                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(int(min_val * scale))
                slider.setMaximum(int(max_val * scale))
                slider.setSingleStep(1)
                slider.setValue(int(default * scale))

                spinbox = create_spinbox(param_type, min_val, max_val, step, default)
                spinbox.setToolTip(param_info.get("description", ""))

                # Sincronización
                if param_type == "float_slider":
                    slider.valueChanged.connect(
                        lambda val, sb=spinbox, sc=scale: sb.setValue(float(val) / sc)
                    )
                else:
                    slider.valueChanged.connect(
                        lambda val, sb=spinbox, sc=scale: sb.setValue(int(val / sc))
                    )
                spinbox.valueChanged.connect(
                    lambda val, sl=slider, sc=scale: sl.setValue(int(val * sc))
                )

                def on_change(val, p=param_name, sb=spinbox):
                    val = float(val) if param_type == "float_slider" else int(val)
                    if must_be_odd and isinstance(val, int) and val % 2 == 0:
                        val += 1
                        slider.setValue(val * scale)
                        spinbox.setValue(val)
                    highlight_if_invalid(sb, min_val <= val <= max_val)
                    self._on_param_changed(p, val)

                slider.valueChanged.connect(lambda val: on_change(val / scale))
                spinbox.valueChanged.connect(on_change)

                row.addWidget(slider)
                row.addWidget(spinbox)
                self.param_widgets[param_name] = (slider, spinbox)
            self.layout.addLayout(row)

    def _on_param_changed(self, param_name: str, value):
        param_info = self.filter_metadata["params"].get(param_name, {})
        range_vals = param_info.get("range", (0, 100))

        if not isinstance(range_vals, (list, tuple)) or len(range_vals) < 2:
            print(f"[⚠️] Rango inválido para '{param_name}': {range_vals}")
            range_vals = (0, 100)

        min_val = range_vals[0]
        max_val = range_vals[1]
        step = range_vals[2] if len(range_vals) > 2 else 1
        must_be_odd = param_info.get("must_be_odd", False)

        # Clamping
        try:
            value = float(value)
            if value < min_val:
                value = min_val
            elif value > max_val:
                value = max_val
        except Exception as e:
            print(f"[❌] Error al validar valor de '{param_name}': {e}")
            return

        # Redondear al múltiplo más cercano del paso
        if isinstance(value, float) and step > 0:
            value = round(round((value - min_val) / step) * step + min_val, 6)

        # Forzar impar si aplica
        if must_be_odd:
            value = int(round(value))
            if value % 2 == 0:
                value += 1

        # Evitar emitir si no hay cambio real
        if self.current_params.get(param_name) == value:
            return

        self.current_params[param_name] = value
        self.params_changed.emit(self.filter_name, self.current_params, self._index)

    def _on_enabled_toggled(self, state):
        self.enabled_toggled.emit(
            self.filter_name, state == Qt.CheckState.Checked, self._index
        )

    def get_filter_config(self) -> dict:
        return {
            "name": self.filter_name,
            "params": self.current_params,
            "enabled": self.enabled_checkbox.isChecked(),
        }

    def set_index(self, new_index: int):
        self._index = new_index

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Duplicar", lambda: self.duplicated.emit(self._index))
        menu.addAction("Eliminar", lambda: self.removed.emit(self._index))
        menu.addAction("Mover arriba", lambda: self.moved.emit(self._index, "up"))
        menu.addAction("Mover abajo", lambda: self.moved.emit(self._index, "down"))
        menu.addAction("Activar/Desactivar", lambda: self.enabled_checkbox.toggle())
        menu.exec(event.globalPos())
