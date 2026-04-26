import os
import glob
import logging
from pathlib import Path
from utils import load_marks_csv, get_pdf_total_pages, save_output_json
from llm_mapper import detect_question_pages

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_batch():
    """
    Scans data/scripts/*.pdf, finds matching CSV in data/marks/,
    runs Gemini detection, and saves results to data/pending/.
    """
    scripts_dir = Path("data/scripts")
    marks_dir = Path("data/marks")
    pending_dir = Path("data/pending")
    
    # Create directories if they don't exist
    pending_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(scripts_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {scripts_dir}")
        return

    logger.info(f"Found {len(pdf_files)} PDF scripts to process.")

    for pdf_path in pdf_files:
        doc_id = pdf_path.stem
        
        # Map PDF (ds_001) to CSV (gt_001)
        # Assuming the suffix after the underscore is the unique ID
        csv_id = doc_id.replace("ds_", "gt_")
        csv_path = marks_dir / f"{csv_id}.csv"
        
        if not csv_path.exists():
            logger.warning(f"Skipping {doc_id}: CSV not found at {csv_path}")
            continue
            
        pending_path = pending_dir / f"{doc_id}.json"
        if pending_path.exists():
            logger.info(f"Skipping {doc_id}: Pending JSON already exists.")
            continue

        logger.info(f"Processing {doc_id}...")
        try:
            # Load question IDs from marks CSV to guide Gemini
            marks_map = load_marks_csv(str(csv_path))
            question_ids = list(marks_map.keys())
            
            # Detect question pages
            detected = detect_question_pages(str(pdf_path), question_ids)
            
            # Add metadata
            detected["document_id"] = doc_id
            detected["total_pages"] = get_pdf_total_pages(str(pdf_path))
            
            # Save candidate ground truth to pending
            save_output_json(detected, str(pending_path))
            logger.info(f"Successfully processed {doc_id} -> {pending_path}")
            
        except Exception as e:
            logger.error(f"Failed to process {doc_id}: {e}")

if __name__ == "__main__":
    run_batch()
