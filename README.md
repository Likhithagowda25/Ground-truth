# Ground Truth Generation Tool (Autonomous & Verified)

An autonomous system for generating and verifying ground-truth JSON for student answer scripts using **Gemini 2.5 Pro (Multimodal)** and **Streamlit**.

## Features

-   **Autonomous Batch Processing**: Automatically scans student script PDFs and marks CSVs to generate initial question-to-page mappings.
-   **Multimodal AI Detection**: Uses Gemini 2.5 Pro vision capabilities to "read" handwritten scripts and detect answer locations.
-   **Intelligent PDF Optimization**: Automatically compresses scripts for LLM processing to reduce latency and cost while maintaining legibility.
-   **Verification Dashboard**:
    -   **Paginated Viewer**: Custom image-based renderer for a stable, fit-to-screen experience.
    -   **Dynamic Layout**: Optimized split view with an expanded table for easy editing.
    -   **Direct Navigation**: Skip to any page instantly via numeric input.
    -   **Bulk Export**: Export all verified scripts in one click or process individual files.
    -   **Custom Paths**: Configure your export directory on the fly.

## Installation

### 1. Prerequisites
- **Python 3.12+**
- **GCloud SDK**: Configured with Application Default Credentials (ADC).
  ```bash
  gcloud auth application-default login
  ```

### 2. Setup
Clone the repository and install dependencies using pip:
```bash
pip install .
```
*(Alternatively, install the required packages: `google-genai`, `streamlit`, `pymupdf`, `pandas`)*

## Usage

### 1. Prepare Data
- Place student PDFs in `data/scripts/` (e.g., `ds_001.pdf`).
- Place matching marks CSVs in `data/marks/` (e.g., `gt_001.csv`).

### 2. Run Batch Detection
Execute the autonomous detector to generate initial mappings:
```bash
python src/batch_processor.py
```
This generates candidate JSON files in `data/pending/`.

### 3. Verify & Export
Launch the dashboard to review and finalize the detections:
```bash
streamlit run src/app.py
```
- Select a script from the **Verification Hub** sidebar.
- Use the **Page Input** to navigate the PDF.
- Edit the **Question Mapping** table as needed (empty page numbers are allowed).
- Click **Export Verified Ground Truth** to save the final JSON to `data/output/`.

---

## Example Formats

### Input: Marks CSV (`gt_001.csv`)
```csv
question_id,marks
1a,6
1b,7
1c,0
```

### Output: Verified JSON (`ds_001.json`)
```json
{
  "document_id": "ds_001",
  "total_pages": 12,
  "questions": [
    {
      "question_id": "1a",
      "pages": [1, 2],
      "obtained_marks": 6
    },
    {
      "question_id": "1b",
      "pages": [3],
      "obtained_marks": 7
    }
  ]
}
```
