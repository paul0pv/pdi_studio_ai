# ui/widgets/filter_control.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from processing.filters import FILTER_METADATA


class FilterControl(QGroupBox):
    """
    A widget to control a single filter's parameters, enable/disable state,
    and provide options to remove or reorder it within the pipeline.
    """

    params_changed = pyqtSignal(str, dict, int)
    enabled_toggled = pyqtSignal(str, bool, int)
    removed = pyqtSignal(int)
    moved = pyqtSignal(int, str)

    def __init__(self, filter_name: str, initial_params: dict, index: int, parent=None):
        super().__init__(filter_name.replace("_", " ").title(), parent)
        self.filter_name = filter_name

        # current_params ONLY holds the filter-specific parameters, not the 'enabled' state
        self.current_params = {
            k: v for k, v in initial_params.items() if k != "enabled"
        }

        self._index = index
        self.filter_metadata = FILTER_METADATA.get(self.filter_name, {})

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(120)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self._build_ui()
        # Initialize checkbox state based on 'enabled' from initial_params (top-level or default True)
        initial_enabled_state = initial_params.get("enabled", True)
        self.enabled_checkbox.setChecked(initial_enabled_state)
        self._update_ui_from_params()

    def _build_ui(self):
        """Constructs the UI elements for the filter control."""
        control_row_layout = QHBoxLayout()
        self.enabled_checkbox = QCheckBox("Enabled")
        # Do not set checked state here; it's set in __init__ after current_params is processed.
        self.enabled_checkbox.stateChanged.connect(self._on_enabled_toggled)
        control_row_layout.addWidget(self.enabled_checkbox)

        control_row_layout.addStretch(1)

        self.move_up_button = QPushButton("↑")
        self.move_up_button.setFixedSize(QSize(25, 25))
        self.move_up_button.clicked.connect(lambda: self.moved.emit(self._index, "up"))
        control_row_layout.addWidget(self.move_up_button)

        self.move_down_button = QPushButton("↓")
        self.move_down_button.setFixedSize(QSize(25, 25))
        self.move_down_button.clicked.connect(
            lambda: self.moved.emit(self._index, "down")
        )
        control_row_layout.addWidget(self.move_down_button)

        self.remove_button = QPushButton("X")
        self.remove_button.setFixedSize(QSize(25, 25))
        self.remove_button.clicked.connect(lambda: self.removed.emit(self._index))
        control_row_layout.addWidget(self.remove_button)

        self.main_layout.addLayout(control_row_layout)

        self.params_layout = QVBoxLayout()
        self.param_widgets = {}

        filter_params_meta = self.filter_metadata.get("params", {})
        if not filter_params_meta:
            self.params_layout.addWidget(QLabel("No configurable parameters."))
        else:
            for param_name, param_info in filter_params_meta.items():
                param_control_widget = self._create_param_control(
                    param_name, param_info
                )
                self.params_layout.addWidget(param_control_widget)
        self.main_layout.addLayout(self.params_layout)

        self.main_layout.addStretch(1)

    def _create_param_control(self, param_name: str, param_info: dict) -> QWidget:
        """
        Creates a control (slider and spinbox) for a single filter parameter.
        Handles both integer and float parameters.
        """
        param_widget = QWidget()
        param_layout = QHBoxLayout(param_widget)
        param_layout.setContentsMargins(0, 0, 0, 0)

        param_layout.addWidget(QLabel(param_info.get("label", param_name) + ":"))

        min_val = param_info["range"][0]
        max_val = param_info["range"][1]
        step = param_info["range"][2]
        default_val = param_info["default"]

        current_param_value = self.current_params.get(param_name, default_val)

        spinbox = None
        slider = None

        if param_info["type"] == "int_slider":
            spinbox = QSpinBox()
            spinbox.setRange(int(min_val), int(max_val))
            spinbox.setSingleStep(int(step))
            spinbox.setValue(int(current_param_value))

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(int(min_val), int(max_val))
            slider.setSingleStep(int(step))
            slider.setValue(int(current_param_value))

            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)

        elif param_info["type"] == "float_slider":
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setSingleStep(step)
            spinbox.setDecimals(2)
            spinbox.setValue(current_param_value)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider_max_val = int((max_val - min_val) / step)
            slider.setRange(0, slider_max_val)
            slider.setSingleStep(1)
            slider.setValue(int((current_param_value - min_val) / step))

            slider.valueChanged.connect(
                lambda val, sbox=spinbox, mv=min_val, st=step: sbox.setValue(
                    mv + val * st
                )
            )
            spinbox.valueChanged.connect(
                lambda val, sld=slider, mv=min_val, st=step: sld.setValue(
                    int((val - mv) / st)
                )
            )

        if spinbox and slider:
            param_layout.addWidget(spinbox)
            param_layout.addWidget(slider)
            self.param_widgets[param_name] = {"spinbox": spinbox, "slider": slider}

            if param_info["type"] == "int_slider":
                spinbox.valueChanged.connect(
                    lambda val, p_name=param_name: self._on_param_changed(p_name, val)
                )
            elif param_info["type"] == "float_slider":
                spinbox.valueChanged.connect(
                    lambda val, p_name=param_name: self._on_param_changed(p_name, val)
                )

        return param_widget

    def _on_param_changed(self, param_name: str, value):
        """Updates the current_params and emits the signal when a parameter changes."""
        self.current_params[param_name] = value
        # Emit signal with current filter name, updated parameters, and its index
        # The 'enabled' state is NOT part of current_params here, but will be added by get_filter_config
        self.params_changed.emit(self.filter_name, self.current_params, self._index)

    def _on_enabled_toggled(self, state: int):
        """Updates the enabled state and emits the signal."""
        is_enabled = bool(state)
        # Emit signal with current filter name, new enabled state, and its index
        self.enabled_toggled.emit(self.filter_name, is_enabled, self._index)
        # Enable/disable parameter controls
        for param_widgets in self.param_widgets.values():
            if "spinbox" in param_widgets:
                param_widgets["spinbox"].setEnabled(is_enabled)
            if "slider" in param_widgets:
                param_widgets["slider"].setEnabled(is_enabled)

    def _update_ui_from_params(self):
        """Updates the UI elements (checkbox, spinboxes, sliders) based on current_params."""
        is_enabled = (
            self.enabled_checkbox.isChecked()
        )  # Read current UI state for controls

        filter_params_meta = self.filter_metadata.get("params", {})
        for param_name, param_info in filter_params_meta.items():
            if param_name in self.param_widgets:
                spinbox = self.param_widgets[param_name]["spinbox"]
                slider = self.param_widgets[param_name]["slider"]

                spinbox.setEnabled(is_enabled)
                slider.setEnabled(is_enabled)

                current_value = self.current_params.get(
                    param_name, param_info["default"]
                )

                if param_info["type"] == "int_slider":
                    spinbox.setValue(int(current_value))
                    slider.setValue(int(current_value))
                elif param_info["type"] == "float_slider":
                    spinbox.setValue(current_value)
                    min_val = param_info["range"][0]
                    step = param_info["range"][2]
                    slider.setValue(int((current_value - min_val) / step))

    def set_index(self, index: int):
        """Updates the internal index of the filter control."""
        self._index = index

    def get_filter_config(self) -> dict:
        """
        Returns the current configuration of this filter,
        with 'enabled' at the top level, and parameters in 'params'.
        """
        is_enabled = self.enabled_checkbox.isChecked()

        # current_params already holds only the filter-specific parameters
        # no need to remove 'enabled' from it here.
        return {
            "name": self.filter_name,
            "params": self.current_params,
            "enabled": is_enabled,
        }

    # --- For standalone testing (optional) ---


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("FilterControl Test")

    test_grayscale_config = {
        "name": "convert_to_grayscale",
        "params": {},  # No params here, enabled will be top-level
        "enabled": True,
    }
    test_brightness_contrast_config = {
        "name": "adjust_brightness_contrast",
        "params": {"alpha": 1.5, "beta": 50},
        "enabled": True,
    }
    test_sepia_config = {
        "name": "sepia_tint",
        "params": {"strength": 0.7},
        "enabled": True,
    }
    test_canny_config = {
        "name": "apply_canny_edge_detection",
        "params": {"low_threshold": 80, "high_threshold": 200},
        "enabled": True,
    }

    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)

    filter1 = FilterControl(
        test_brightness_contrast_config["name"],
        test_brightness_contrast_config["params"],
        0,
    )
    # The __init__ now takes care of setting initial checkbox state.
    # filter1.enabled_checkbox.setChecked(test_brightness_contrast_config["enabled"])
    filter1.params_changed.connect(
        lambda n, p, i: print(f"Filter1 Params Changed: {n}, {p}, Index: {i}")
    )
    filter1.enabled_toggled.connect(
        lambda n, e, i: print(f"Filter1 Enabled Toggled: {n}, {e}, Index: {i}")
    )
    filter1.removed.connect(lambda i: print(f"Filter1 Removed at Index: {i}"))
    filter1.moved.connect(lambda i, d: print(f"Filter1 Moved: {i}, {d}"))
    main_layout.addWidget(filter1)

    filter2 = FilterControl(test_sepia_config["name"], test_sepia_config["params"], 1)
    # filter2.enabled_checkbox.setChecked(test_sepia_config["enabled"])
    filter2.params_changed.connect(
        lambda n, p, i: print(f"Filter2 Params Changed: {n}, {p}, Index: {i}")
    )
    filter2.enabled_toggled.connect(
        lambda n, e, i: print(f"Filter2 Enabled Toggled: {n}, {e}, Index: {i}")
    )
    filter2.removed.connect(lambda i: print(f"Filter2 Removed at Index: {i}"))
    filter2.moved.connect(lambda i, d: print(f"Filter2 Moved: {i}, {d}"))
    main_layout.addWidget(filter2)

    filter3 = FilterControl(test_canny_config["name"], test_canny_config["params"], 2)
    # filter3.enabled_checkbox.setChecked(test_canny_config["enabled"])
    filter3.params_changed.connect(
        lambda n, p, i: print(f"Filter3 Params Changed: {n}, {p}, Index: {i}")
    )
    filter3.enabled_toggled.connect(
        lambda n, e, i: print(f"Filter3 Enabled Toggled: {n}, {e}, Index: {i}")
    )
    filter3.removed.connect(lambda i: print(f"Filter3 Removed at Index: {i}"))
    filter3.moved.connect(lambda i, d: print(f"Filter3 Moved: {i}, {d}"))
    main_layout.addWidget(filter3)

    filter4 = FilterControl(
        test_grayscale_config["name"], test_grayscale_config["params"], 3
    )
    # filter4.enabled_checkbox.setChecked(test_grayscale_config["enabled"])
    filter4.params_changed.connect(
        lambda n, p, i: print(f"Filter4 Params Changed: {n}, {p}, Index: {i}")
    )
    filter4.enabled_toggled.connect(
        lambda n, e, i: print(f"Filter4 Enabled Toggled: {n}, {e}, Index: {i}")
    )
    filter4.removed.connect(lambda i: print(f"Filter4 Removed at Index: {i}"))
    filter4.moved.connect(lambda i, d: print(f"Filter4 Moved: {i}, {d}"))
    main_layout.addWidget(filter4)

    main_layout.addStretch(1)

    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())
