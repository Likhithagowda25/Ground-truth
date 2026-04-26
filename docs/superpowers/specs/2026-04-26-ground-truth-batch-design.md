# Design Doc: Ground Truth Batch Generation & Verification

## Overview
A system to autonomously generate ground-truth JSON for student answer scripts using **Gemini 2.5 Pro (Multimodal)**. The system processes files in batch via a CLI script and provides a Streamlit dashboard for final human verification and export.

## Architecture
- **Engine:** Python with Vertex AI SDK.
- **Model:** `gemini-2.5-pro` (Multimodal PDF support).
- **Auth:** System-level `gcloud` Application Default Credentials (ADC).
- **Storage:** Local file system (`data/scripts`, `data/marks`, `data/pending`, `data/output`).

## Components

### 1. Batch Processor (CLI)
- **Input:** Scans `data/scripts/*.pdf` and `data/marks/*.csv`.
- **Logic:**
  - Extracts expected Question IDs from the CSV.
  - Sends the PDF file directly to Gemini 2.5 Pro as a multimodal prompt.
  - Asks Gemini to find specific page numbers for each Question ID.
- **Output:** Saves a candidate JSON to `data/pending/<id>.json`.

### 2. Verification Dashboard (Streamlit)
- **Input:** Reads files from `data/pending/`.
- **Logic:**
  - Lists all pending scripts for review.
  - Displays an editable table of Question -> Page mappings.
  - Merges mapping with marks from the CSV for full ground-truth preview.
- **Output:** Exports verified JSON to `data/output/` and removes it from `pending/`.

## Data Schema (Output)
```json
{
  "document_id": "gt_001",
  "total_pages": 12,
  "questions": [
    {
      "question_id": "Q1a",
      "pages": [1, 2],
      "obtained_marks": 6
    }
  ]
}
```

## Success Criteria
- **Accuracy:** Gemini 2.5 Pro correctly identifies page numbers for 90%+ of questions.
- **Efficiency:** Batch processing reduces wait time in the UI.
- **Security:** Uses local `gcloud` auth; no secrets committed.
