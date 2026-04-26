# Ground-Truth Generator & Verifier

A multimodal AI tool powered by Gemini 2.5 Pro for autonomous generation and manual verification of student answer script ground-truth JSONs.

## Features
- **AI-Guided Detection**: Automatically maps question IDs to physical PDF pages using Gemini 2.5 Pro.
- **Recursive Directory Support**: Organize your scripts and marks in nested folders (e.g., by class, subject, or year). The tool preserves this structure throughout the pipeline.
- **Verification Dashboard**: A Streamlit-based UI to review AI predictions alongside the original PDF.
- **Bulk Processing**: CLI tool for high-volume candidate generation.
- **Smart Compression**: Automatically optimizes PDFs for LLM processing to reduce latency and costs.

## Directory Structure
The tool expects the following structure in the `data/` directory:

```text
data/
├── scripts/             # Input student answer scripts (PDF)
│   └── [subfolders]/    # (Optional) Nested organization
├── marks/               # Input marks CSVs (must match script filename prefix)
│   └── [subfolders]/    # (Optional) Must match scripts subfolder structure
├── pending/             # Generated candidate JSONs (auto-created)
└── output/              # Final verified ground-truth JSONs (auto-created)
```

**Note**: Files in `scripts/` (e.g., `ds_001.pdf`) are matched with files in `marks/` (e.g., `gt_001.csv`) using the `ds_` to `gt_` prefix mapping.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Ground-truth
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install .
   ```

4. **Authentication**:
   Ensure you have `gcloud` ADC configured:
   ```bash
   gcloud auth application-default login
   ```

## Usage

### 1. Batch Generation
Place your PDFs in `data/scripts/` and matching CSVs in `data/marks/`. Then run:
```bash
python src/batch_processor.py
```
Candidates will be generated in `data/pending/`.

### 2. Manual Verification
Launch the verification dashboard:
```bash
streamlit run src/app.py
```
- Select a script from the sidebar or use the **Prev/Next** buttons.
- Review the PDF and edit the question-to-page mappings in the table.
- Click **Export Verified Ground Truth** to save the final JSON to `data/output/`.

## Input Schema
- **Marks CSV**: Must contain `question_id` (lowercase) and `obtained_marks` columns.
- **PDF Scripts**: Standard student answer scripts.
