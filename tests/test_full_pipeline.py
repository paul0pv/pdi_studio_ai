# test_full_pipeline.py
import pytest
from llm.pipeline_generator import generate_pipeline


def test_pipeline_generation_all_styles(sample_queries):
    for style, query in sample_queries.items():
        pipeline = generate_pipeline(query)
        print(f"\n[{style}] → Entrada: {query}")
        print(f"Pipeline: {pipeline}")
        assert pipeline is not None
        assert isinstance(pipeline, list)
        assert all("name" in f for f in pipeline)
        assert all("params" in f for f in pipeline)
