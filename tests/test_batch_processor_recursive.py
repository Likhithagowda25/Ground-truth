import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

from batch_processor import run_batch

def test_run_batch_recursive_structure(tmp_path):
    # Setup mock directory structure in tmp_path
    scripts_root = tmp_path / "data" / "scripts"
    marks_root = tmp_path / "data" / "marks"
    pending_root = tmp_path / "data" / "pending"
    
    sub_dir = "class_A"
    (scripts_root / sub_dir).mkdir(parents=True)
    (marks_root / sub_dir).mkdir(parents=True)
    pending_root.mkdir(parents=True)
    
    pdf_path = scripts_root / sub_dir / "ds_001.pdf"
    pdf_path.touch()
    
    csv_path = marks_root / sub_dir / "gt_001.csv"
    csv_path.touch()
    
    # Patch Path.cwd() to return our tmp_path
    with patch("batch_processor.Path.cwd", return_value=tmp_path):
        with patch("batch_processor.load_marks_csv") as mock_load_csv, \
             patch("batch_processor.compress_pdf") as mock_compress, \
             patch("batch_processor.detect_question_pages") as mock_detect, \
             patch("batch_processor.save_output_json") as mock_save, \
             patch("batch_processor.get_pdf_total_pages") as mock_total_pages, \
             patch("batch_processor.os.remove"):
            
            mock_load_csv.return_value = {"Q1": 1}
            mock_detect.return_value = {"results": []}
            mock_total_pages.return_value = 5
            
            run_batch()
            
            # Verify mirrored paths
            expected_pending_path = pending_root / sub_dir / "ds_001.json"
            
            # Check if save_output_json was called with the correct path
            mock_save.assert_called_once()
            args, _ = mock_save.call_args
            # args[1] is the pending_path
            assert Path(args[1]) == expected_pending_path
