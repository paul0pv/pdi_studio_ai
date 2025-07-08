# ui/main_window/layout_pipeline_tabs.py

from PyQt6.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QSplitter
from ui.widgets.filter_selector import FilterSelector
from ui.widgets.pipeline_manager import PipelineManager
from ui.widgets.preset_selector import PresetSelector
from ui.widgets.favorites_tab import FavoritesTab
from ui.widgets.style_input_preview import StyleInputPreview
from ui.main_window.layout_llm_group import build_llm_group


@property
def filter_metadata(self):
    from processing import filters

    return filters.FILTER_METADATA


def build_pipeline_tabs(main_window):
    layout = QVBoxLayout()
    main_window.pipeline_tabs = QTabWidget()

    # Manual tab
    manual_tab = QWidget()
    manual_layout = QVBoxLayout(manual_tab)
    main_window.filter_selector = FilterSelector()
    main_window.filter_selector.set_available_filters(
        list(main_window.image_processor.available_filters.keys()),
        main_window.image_processor.filter_metadata,
    )
    main_window.pipeline_manager = PipelineManager()
    main_window.preset_selector = PresetSelector()
    splitter = QSplitter()
    splitter.addWidget(main_window.pipeline_manager)
    splitter.addWidget(main_window.preset_selector)
    manual_layout.addWidget(main_window.filter_selector)
    manual_layout.addWidget(splitter)

    # LLM tab
    llm_tab = QWidget()
    llm_layout = QVBoxLayout(llm_tab)
    main_window.llm_group_box = build_llm_group(main_window)
    main_window.style_preview_widget = StyleInputPreview(
        main_window.camera_feed, main_window.pipeline_generator
    )
    llm_layout.addWidget(main_window.llm_group_box)
    llm_layout.addWidget(main_window.style_preview_widget)

    # Favoritos tab
    main_window.favorites_tab = FavoritesTab(main_window._apply_preset_from_selector)

    main_window.pipeline_tabs.addTab(manual_tab, "Manual")
    main_window.pipeline_tabs.addTab(llm_tab, "Asistente LLM")
    main_window.pipeline_tabs.addTab(main_window.favorites_tab, "Favoritos")

    layout.addWidget(main_window.pipeline_tabs)
    return layout
