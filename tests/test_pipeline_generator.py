# test_pipeline_generator.py
from llm.pipeline_generator import generate_pipeline


def test_pipeline_generation_basic():
    query = "Quiero imagen estilo retrato con fondo desenfocado y tono cálido"
    pipeline = generate_pipeline(query)
    assert pipeline is not None
    assert any(f["name"] == "bokeh_effect" for f in pipeline)
    assert any(f["name"] == "sepia_tint" for f in pipeline)
