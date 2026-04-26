# Ground Truth Generation & Verification Tool

A tool to autonomously generate ground-truth JSON for student answer scripts using Google Gemini (Vertex AI), with a Streamlit interface for quick verification.

## Features

1. **Autonomous Mapping**: Gemini analyzes the PDF answer script and automatically maps questions to page numbers.
2. **Marks Integration**: Merges detected questions with marks from a provided CSV.
3. **Verification UI**: Streamlit interface to review, edit, and verify Gemini's output.
4. **Vertex AI Support**: Uses system-level authentication (`gcloud`) for secure access.

## Project Structure

```text
Ground-truth/
├── data/
│   ├── scripts/   # Uploaded PDFs
│   ├── marks/     # Uploaded CSVs
│   └── output/    # Generated JSONs
├── src/
│   ├── app.py          # Streamlit Verification UI
│   ├── llm_mapper.py   # Vertex AI / Gemini Logic
│   └── utils.py        # File & Data Utilities
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

1. **GCloud Auth**: Ensure you have `gcloud` installed and authenticated:
   ```bash
   gcloud auth application-default login
   ```
2. **Environment**: Set your Google Cloud Project ID:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```
3. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the verification tool:
```bash
streamlit run src/app.py
```

1. Upload PDF & CSV.
2. Click **Run Gemini Detection**.
3. Verify/Edit the generated mapping in the table.
4. Click **Export Verified Ground Truth**.

## CSV Format

```csv
question_id,marks
1a,6
1b,7
```
*Note: `question_id` in CSV should match the suffix of Gemini's detection (e.g., if Gemini finds `Q1a`, CSV should have `1a`).*
