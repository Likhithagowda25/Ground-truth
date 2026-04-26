# Ground Truth Batch Generation & Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Autonomously generate ground-truth JSON for student answer scripts using multimodal Gemini 2.5 Pro in batch, with a Streamlit verification dashboard.

**Architecture:** A CLI-based batch processor for detection and a Streamlit-based dashboard for human verification. Uses system-level `gcloud` auth and multimodal PDF input for high accuracy.

**Tech Stack:** Python, Vertex AI SDK (Gemini 2.5 Pro), Pandas, PyMuPDF, Streamlit.

---

### Task 1: Environment & Directory Setup

**Files:**
- Create: `data/pending/.gitkeep`
- Create: `data/output/.gitkeep`
- Modify: `requirements.txt`

- [ ] **Step 1: Update requirements.txt**

Ensure all necessary libraries are included.

```text
streamlit
pymupdf
pandas
google-cloud-aiplatform
```

- [ ] **Step 2: Create necessary directories**

```bash
mkdir -p data/pending data/output
touch data/pending/.gitkeep data/output/.gitkeep
```

- [ ] **Step 3: Commit setup**

```bash
git add requirements.txt data/pending/.gitkeep data/output/.gitkeep
git commit -m "chore: setup project directories and requirements"
```

### Task 2: Multimodal Gemini Mapper (Core Logic)

**Files:**
- Modify: `src/llm_mapper.py`

- [ ] **Step 1: Update Prompt for Multimodal Input**

Modify `LLM_PROMPT_TEMPLATE` to accept a list of expected question IDs and request strict JSON.

```python
LLM_PROMPT_TEMPLATE = """You are an expert at analyzing student answer scripts.
I am providing you with a PDF of a student's handwritten answer script.
Your task is to identify the exact page numbers where each of the following questions are answered.

Expected Question IDs: {question_ids}

Rules:
- Use page numbers starting from 1.
- If a question spans multiple pages, list all of them: [1, 2].
- Return ONLY a valid JSON object.
- Use the exact Question IDs provided above.

Format:
{{
  "questions": [
    {{"question_id": "1a", "pages": [1, 2]}},
    {{"question_id": "1b", "pages": [3]}}
  ]
}}
"""
```

- [ ] **Step 2: Implement Multimodal Content Generation**

Update `detect_questions_from_pdf` to use the Vertex AI `Part` API for PDF input.

```python
from vertexai.generative_models import GenerativeModel, Part

def detect_questions_from_pdf(pdf_path: str, question_ids: list, model_name: str = "gemini-2.5-pro") -> str:
    vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")
    model = GenerativeModel(model_name)
    
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    
    pdf_part = Part.from_data(data=pdf_data, mime_type="application/pdf")
    prompt = LLM_PROMPT_TEMPLATE.format(question_ids=", ".join(question_ids))
    
    response = model.generate_content([pdf_part, prompt])
    return response.text
```

- [ ] **Step 3: Update detect_question_pages for Batch Use**

```python
def detect_question_pages(pdf_path: str, question_ids: list, model: str = "gemini-2.5-pro") -> Dict[str, Any]:
    text_output = detect_questions_from_pdf(pdf_path, question_ids, model_name=model)
    parsed = _extract_json(text_output)
    return parsed
```

- [ ] **Step 4: Commit Gemini logic**

```bash
git add src/llm_mapper.py
git commit -m "feat: implement multimodal Gemini detection with guided question IDs"
```

### Task 3: Batch Processing Script (CLI)

**Files:**
- Create: `src/batch_processor.py`

- [ ] **Step 1: Implement Batch Logic**

Iterate through `data/scripts/*.pdf`, find matching `data/marks/*.csv`, run Gemini, and save to `data/pending/`.

```python
import os
import glob
from pathlib import Path
from utils import load_marks_csv, get_pdf_total_pages, save_output_json
from llm_mapper import detect_question_pages

def run_batch():
    scripts = glob.glob("data/scripts/*.pdf")
    for pdf_path in scripts:
        doc_id = Path(pdf_path).stem
        csv_path = f"data/marks/{doc_id.replace('ds_', 'gt_')}.csv" # Adjusted for your naming convention
        
        if not os.path.exists(csv_path):
            print(f"Skipping {doc_id}, CSV not found at {csv_path}")
            continue
            
        print(f"Processing {doc_id}...")
        marks_map = load_marks_csv(csv_path)
        question_ids = list(marks_map.keys())
        
        try:
            detected = detect_question_pages(pdf_path, question_ids)
            detected["document_id"] = doc_id
            detected["total_pages"] = get_pdf_total_pages(pdf_path)
            
            output_path = f"data/pending/{doc_id}.json"
            save_output_json(detected, output_path)
            print(f"Saved to {output_path}")
        except Exception as e:
            print(f"Failed to process {doc_id}: {e}")

if __name__ == "__main__":
    run_batch()
```

- [ ] **Step 2: Commit Batch Processor**

```bash
git add src/batch_processor.py
git commit -m "feat: add batch processing script"
```

### Task 4: Verification Dashboard (Streamlit)

**Files:**
- Modify: `src/app.py`

- [ ] **Step 1: Implement "Pending" File Selection**

Allow user to select from files in `data/pending/`.

```python
import glob
import streamlit as st

pending_files = glob.glob("data/pending/*.json")
selected_json = st.selectbox("Select a script to verify", pending_files)
```

- [ ] **Step 2: Merge Pending Detection with CSV Marks**

```python
if selected_json:
    with open(selected_json, "r") as f:
        data = json.load(f)
    
    doc_id = data["document_id"]
    csv_path = f"data/marks/{doc_id.replace('ds_', 'gt_')}.csv"
    marks_map = load_marks_csv(csv_path)
    
    # Use existing merge_questions_with_marks utility
    merged = merge_questions_with_marks(data["questions"], marks_map)
    # ... display in data_editor ...
```

- [ ] **Step 3: Final Export Logic**

When "Export Verified Ground Truth" is clicked, save to `data/output/` and delete from `data/pending/`.

```python
# ... inside export button logic ...
save_output_json(final_payload, output_path)
os.remove(selected_json)
st.success(f"Exported and removed from pending: {doc_id}")
```

- [ ] **Step 4: Commit UI changes**

```bash
git add src/app.py
git commit -m "feat: update Streamlit UI for batch verification workflow"
```
