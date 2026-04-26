# Ground Truth Generation Tool

Minimal Streamlit app to generate ground-truth JSON for student answer scripts.

## What it does

1. Upload one multi-page answer script PDF
2. Upload marks CSV
3. Auto-detect question-to-page mapping using Google Gemini
4. Merge detected questions with marks
5. Manually edit in UI
6. Export final JSON to `data/output/`

## Project Structure

```text
project/
├── data/
│   ├── scripts/
│   ├── marks/
│   └── output/
├── src/
│   ├── app.py
│   ├── llm_mapper.py
│   └── utils.py
├── requirements.txt
├── .gitignore
└── README.md
```

## CSV Format (Exact)

```csv
question_id,marks
1a,6
1b,7
1c,0
```

Rules:
- `question_id` must be lowercase
- `marks` must be integer
- CSV can have any filename (it is used directly as uploaded)

## Setup

1. Create and activate virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set Gemini API key:

```bash
set GOOGLE_API_KEY=your_api_key_here
```

## Run

From inside `project/`:

```bash
streamlit run src/app.py
```

## Output Format

```json
{
  "document_id": "M1_T2_1",
  "total_pages": 7,
  "questions": [
    {
      "question_id": "Q1a",
      "pages": [1, 2],
      "obtained_marks": 6
    }
  ]
}
```

## Notes

- First version is intentionally simple and supports one PDF + one CSV per run.
- If question is not found in CSV, default `obtained_marks` is `0`.
