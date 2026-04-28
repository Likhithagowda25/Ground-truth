import os
import logging
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from utils import load_marks_csv, get_pdf_total_pages, save_output_json, compress_pdf
from llm_mapper import detect_question_pages

# Configure logging
logger = logging.getLogger(__name__)

def process_single_script(
    pdf_path: Path, 
    rel_path: Path, 
    doc_id: str, 
    scripts_root: Path, 
    marks_root: Path, 
    pending_root: Path, 
    base_dir: Path
):
    """Worker function for a single PDF script."""
    # Map PDF (ds_001) to CSV (gt_001) in the matching subfolder
    csv_id = doc_id.replace("ds_", "gt_")
    csv_path = marks_root / rel_path / f"{csv_id}.csv"
    pending_path = pending_root / rel_path / f"{doc_id}.json"
    
    if not csv_path.exists():
        logger.warning(f"Skipping {doc_id}: Marks CSV not found at {csv_path}")
        return

    logger.info(f"--- Processing: {pdf_path.relative_to(scripts_root)} ---")
    compressed_path = None
    try:
        # Load question IDs
        marks_map = load_marks_csv(str(csv_path))
        question_ids = list(marks_map.keys())
        
        # Compress PDF for LLM
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            compressed_path = tmp_pdf.name
        
        logger.info(f"[{doc_id}] Compressing for LLM...")
        compress_pdf(str(pdf_path), compressed_path)
        
        # Detect question pages
        logger.info(f"[{doc_id}] Running Gemini detection...")
        detected = detect_question_pages(compressed_path, question_ids)
        
        # Add metadata
        detected["document_id"] = doc_id
        detected["total_pages"] = get_pdf_total_pages(str(pdf_path))
        
        # Ensure target directory exists
        pending_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save candidate
        save_output_json(detected, str(pending_path))
        logger.info(f"[{doc_id}] SUCCESS -> {pending_path.relative_to(base_dir)}")
        
    except Exception as e:
        logger.error(f"[{doc_id}] FAILED: {e}")
    finally:
        # Cleanup temp file
        if compressed_path and os.path.exists(compressed_path):
            os.remove(compressed_path)

def run_batch() -> None:
    """
    Scans data/scripts/**/*.pdf, finds matching CSV in data/marks/ (mirrored structure),
    runs Gemini detection, and saves results to data/pending/ (mirrored structure).
    """
    # Use absolute paths to avoid any ambiguity during exists() checks
    base_dir = Path.cwd()
    scripts_root = base_dir / "data" / "scripts"
    marks_root = base_dir / "data" / "marks"
    pending_root = base_dir / "data" / "pending"
    
    # Use rglob for recursive discovery
    pdf_files = sorted(list(scripts_root.rglob("*.pdf")))
    if not pdf_files:
        logger.warning(f"No PDF files found in {scripts_root}")
        return

    logger.info(f"Checking {len(pdf_files)} PDF scripts...")

    # First, filter out files that already have pending JSONs
    to_process = []
    for pdf_path in pdf_files:
        rel_path = pdf_path.relative_to(scripts_root).parent
        doc_id = pdf_path.stem
        pending_path = pending_root / rel_path / f"{doc_id}.json"
        
        if pending_path.exists():
            continue
        to_process.append((pdf_path, rel_path, doc_id))

    if not to_process:
        logger.info("All scripts already have pending JSONs. Nothing to do.")
        return

    max_workers = os.cpu_count() or 4
    logger.info(f"Starting multithreaded processing for {len(to_process)} scripts with {max_workers} workers.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for pdf_path, rel_path, doc_id in to_process:
            executor.submit(
                process_single_script,
                pdf_path,
                rel_path,
                doc_id,
                scripts_root,
                marks_root,
                pending_root,
                base_dir
            )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    run_batch()
