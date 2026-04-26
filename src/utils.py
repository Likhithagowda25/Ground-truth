import json
import os
from typing import Dict, List

import fitz
import pandas as pd


def get_pdf_total_pages(pdf_path: str) -> int:
    doc = fitz.open(pdf_path)
    try:
        return len(doc)
    finally:
        doc.close()


def load_marks_csv(csv_path: str) -> Dict[str, int]:
    df = pd.read_csv(csv_path)
    expected_columns = ["question_id", "marks"]
    if list(df.columns) != expected_columns:
        raise ValueError("CSV must have exact columns: question_id,marks")

    marks_map: Dict[str, int] = {}
    for _, row in df.iterrows():
        question_id = str(row["question_id"]).strip()
        marks_raw = row["marks"]

        if question_id.lower() != question_id:
            raise ValueError(f"question_id must be lowercase: {question_id}")
        if not question_id:
            raise ValueError("question_id cannot be empty.")
        if pd.isna(marks_raw):
            raise ValueError(f"marks missing for question_id {question_id}")

        try:
            marks = int(marks_raw)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"marks must be integers for question_id {question_id}") from exc

        marks_map[question_id] = marks

    return marks_map


def parse_pages_value(value) -> List[int]:
    if isinstance(value, list):
        pages = [int(x) for x in value]
    else:
        raw = str(value).strip()
        if not raw:
            return []
        parts = [x.strip() for x in raw.split(",") if x.strip()]
        pages = [int(x) for x in parts]
    return sorted(set(pages))


def merge_questions_with_marks(detected_questions: List[Dict], marks_map: Dict[str, int]) -> List[Dict]:
    merged: List[Dict] = []
    for q in detected_questions:
        question_id = str(q.get("question_id", "")).strip()
        pages = parse_pages_value(q.get("pages", []))
        key = question_id[1:] if question_id.startswith("Q") else question_id
        key = key.lower()
        obtained_marks = marks_map.get(key, 0)

        merged.append(
            {
                "question_id": question_id,
                "pages": pages,
                "obtained_marks": int(obtained_marks),
            }
        )
    return merged


def build_output_json(document_id: str, total_pages: int, questions: List[Dict]) -> Dict:
    return {
        "document_id": document_id,
        "total_pages": total_pages,
        "questions": questions,
    }


def save_output_json(output_data: Dict, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
