import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
from batch_processor import process_single_script

import logging

def test_process_single_script_missing_csv(tmp_path, caplog):
    # Setup paths
    scripts_root = tmp_path / "scripts"
    marks_root = tmp_path / "marks"
    pending_root = tmp_path / "pending"
    scripts_root.mkdir()
    marks_root.mkdir()
    pending_root.mkdir()

    pdf_path = scripts_root / "ds_test.pdf"
    pdf_path.touch()
    
    # Run worker (should skip and log warning since CSV is missing)
    with caplog.at_level(logging.WARNING):
        process_single_script(
            pdf_path=pdf_path,
            rel_path=Path("."),
            doc_id="ds_test",
            scripts_root=scripts_root,
            marks_root=marks_root,
            pending_root=pending_root,
            base_dir=tmp_path
        )
    
    # Verify no JSON was created
    assert not (pending_root / "ds_test.json").exists()
    assert "Skipping ds_test: Marks CSV not found" in caplog.text

@patch("batch_processor.load_marks_csv")
@patch("batch_processor.compress_pdf")
@patch("batch_processor.detect_question_pages")
@patch("batch_processor.get_pdf_total_pages")
@patch("batch_processor.save_output_json")
def test_process_single_script_success(
    mock_save, mock_get_total, mock_detect, mock_compress, mock_load_csv, tmp_path
):
    # Setup paths
    scripts_root = tmp_path / "scripts"
    marks_root = tmp_path / "marks"
    pending_root = tmp_path / "pending"
    scripts_root.mkdir()
    marks_root.mkdir()
    pending_root.mkdir()

    pdf_path = scripts_root / "ds_001.pdf"
    pdf_path.touch()
    csv_path = marks_root / "gt_001.csv"
    csv_path.touch()

    # Configure mocks
    mock_load_csv.return_value = {"1a": 5, "1b": 5}
    mock_detect.return_value = {
        "questions": [
            {"question_id": "1a", "pages": [1]},
            {"question_id": "1b", "pages": [2]}
        ]
    }
    mock_get_total.return_value = 10

    # Run worker
    process_single_script(
        pdf_path=pdf_path,
        rel_path=Path("."),
        doc_id="ds_001",
        scripts_root=scripts_root,
        marks_root=marks_root,
        pending_root=pending_root,
        base_dir=tmp_path
    )

    # Verify mocks were called
    mock_load_csv.assert_called_once_with(str(csv_path))
    mock_compress.assert_called_once()
    mock_detect.assert_called_once_with(ANY, ["1a", "1b"])
    mock_get_total.assert_called_once_with(str(pdf_path))
    
    # Verify JSON was saved with correct structure
    mock_save.assert_called_once()
    saved_data = mock_save.call_args[0][0]
    assert saved_data["document_id"] == "ds_001"
    assert saved_data["total_pages"] == 10
    assert len(saved_data["questions"]) == 2
