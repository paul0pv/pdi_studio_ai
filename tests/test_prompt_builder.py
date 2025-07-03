# test_prompt_builder.py
from llm.prompt_builder import build_prompt
from processing.filters import FILTER_METADATA


def test_prompt_structure():
    user_query = "Quiero un efecto vintage con sepia y poca saturación"
    subset_metadata = {
        "adjust_saturation": FILTER_METADATA["adjust_saturation"],
        "sepia_tint": FILTER_METADATA["sepia_tint"],
    }
    prompt = build_prompt(user_query, subset_metadata)
    assert "adjust_saturation" in prompt
    assert "sepia_tint" in prompt
    assert "Petición del usuario" in prompt
    assert "filters_identified" in prompt
