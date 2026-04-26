# Ground Truth Batch Generation & Verification Plan

1. **Environment Setup:** Use `uv` to initialize the project, create a `.venv`, and manage dependencies in `pyproject.toml`.
2. **Core Logic:** Update `src/llm_mapper.py` to use `gemini-1.5-pro` with multimodal PDF input for autonomous question-to-page mapping.
3. **Batch Processing:** Create `src/batch_processor.py` to process all PDF/CSV pairs in `data/` and save candidate JSONs to `data/pending/`.
4. **Verification UI:** Update `src/app.py` (Streamlit) to review pending JSONs and export verified results to `data/output/`.