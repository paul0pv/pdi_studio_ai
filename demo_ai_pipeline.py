# script_demo_pipeline.py

from llm.pipeline_generator import generate_pipeline

user_prompt = (
    "Me gustaría una imagen estilo cine noir, con sombras profundas y mucho contraste"
)
pipeline = generate_pipeline(user_prompt)

if pipeline:
    print("\n🎬 Pipeline sugerida para la entrada:")
    for step in pipeline:
        print(f"→ {step['name']} | Params: {step['params']}")
else:
    print("\n⚠️ No se pudo generar una pipeline válida para esa entrada.")
