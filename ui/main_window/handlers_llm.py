# ui/main_window/handlers_llm.py

from llm.llm_worker import LLMWorker


def setup_llm_handlers(main_window):
    main_window.llm_generate_button.clicked.connect(
        lambda: _generate_pipeline_with_llm(main_window)
    )


def _generate_pipeline_with_llm(main_window):
    prompt = main_window.llm_prompt_input.text().strip()
    main_window.style_preview_widget.set_prompt(prompt)

    if not prompt:
        main_window.show_status_message("⚠️ Ingresa una descripción para el LLM.")
        return

    main_window.llm_generate_button.setEnabled(False)
    main_window.llm_prompt_input.setEnabled(False)
    main_window.pipeline_manager.setEnabled(False)

    main_window.llm_status_label.setText("LLM: Procesando...")
    if main_window.llm_movie.isValid():
        main_window.llm_loading_spinner.show()
        main_window.llm_movie.start()

    main_window.pipeline_generator.debug = main_window.debug_checkbox.isChecked()
    main_window.pipeline_generator.temperature = main_window.temperature_input.value()

    worker = LLMWorker(main_window.pipeline_generator, prompt)
    worker.pipeline_ready.connect(lambda p: _on_pipeline_ready(main_window, p))
    worker.fallback_used.connect(
        lambda s: main_window.show_status_message(f"⚠️ Fallback usado: {s}")
    )
    worker.error_occurred.connect(
        lambda m: main_window.show_status_message(f"❌ Error LLM: {m}")
    )
    worker.finished.connect(lambda: _on_llm_finished(main_window))
    main_window.llm_worker = worker
    worker.start()


def _on_pipeline_ready(main_window, pipeline):
    main_window.apply_pipeline(pipeline, source="LLM")
    main_window.llm_status_label.setText("LLM: Pipeline generada.")


def _on_llm_finished(main_window):
    main_window.llm_generate_button.setEnabled(True)
    main_window.llm_prompt_input.setEnabled(True)
    main_window.pipeline_manager.setEnabled(True)
    if main_window.llm_movie.isValid():
        main_window.llm_movie.stop()
        main_window.llm_loading_spinner.hide()
