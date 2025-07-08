# ui/main_window/handlers_pipeline.py


def setup_pipeline_handlers(main_window):
    main_window.filter_selector.filter_selected_to_add.connect(
        lambda name: _add_filter_to_pipeline(main_window, name)
    )
    main_window.preset_selector.set_pipeline_source(
        main_window.pipeline_manager.get_current_pipeline_config
    )
    main_window.preset_selector.preset_applied.connect(
        lambda name, pipeline: _apply_preset(main_window, name, pipeline)
    )
    main_window.pipeline_manager.pipeline_updated.connect(
        lambda config: main_window.image_processor.set_pipeline(config)
    )


def _add_filter_to_pipeline(main_window, filter_name):
    main_window.pipeline_manager.add_filter_to_pipeline(filter_name)
    main_window.show_status_message(f"Filtro '{filter_name}' añadido.")


def _apply_preset(main_window, name, pipeline):
    main_window.apply_pipeline(pipeline, source=f"preset '{name}'")
