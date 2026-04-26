import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from llm_mapper import detect_question_pages
from utils import (
    build_output_json,
    get_pdf_total_pages,
    load_marks_csv,
    merge_questions_with_marks,
    parse_pages_value,
    save_output_json,
)


st.set_page_config(page_title="Ground Truth Generator", layout="centered")
st.title("Ground Truth Generation Tool")
st.write("Upload one PDF and one marks CSV to generate question-wise JSON.")

pdf_file = st.file_uploader("Upload Answer Script PDF", type=["pdf"])
csv_file = st.file_uploader("Upload Marks CSV", type=["csv"])

if "editable_df" not in st.session_state:
    st.session_state.editable_df = pd.DataFrame(columns=["question_id", "pages", "obtained_marks"])
if "document_id" not in st.session_state:
    st.session_state.document_id = ""
if "total_pages" not in st.session_state:
    st.session_state.total_pages = 0


def _validate_questions_for_export(df: pd.DataFrame):
    errors = []
    for idx, row in df.iterrows():
        question_id = str(row.get("question_id", "")).strip() or f"row_{idx + 1}"
        raw_pages = row.get("pages", "")
        try:
            pages = parse_pages_value(raw_pages)
        except Exception:
            errors.append(f"{question_id} (invalid pages format)")
            continue
        if not pages:
            errors.append(f"{question_id} (missing pages)")
    return errors


if st.button("Auto Detect Questions"):
    if not pdf_file or not csv_file:
        st.error("Please upload both PDF and CSV files.")
    else:
        try:
            document_id = Path(pdf_file.name).stem

            scripts_dir = Path("data/scripts")
            marks_dir = Path("data/marks")
            scripts_dir.mkdir(parents=True, exist_ok=True)
            marks_dir.mkdir(parents=True, exist_ok=True)

            pdf_path = scripts_dir / pdf_file.name
            csv_path = marks_dir / csv_file.name
            pdf_path.write_bytes(pdf_file.getbuffer())
            csv_path.write_bytes(csv_file.getbuffer())

            marks_map = load_marks_csv(str(csv_path))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(pdf_file.getbuffer())
                temp_pdf_path = tmp_pdf.name

            detected = detect_question_pages(temp_pdf_path)
            total_pages = get_pdf_total_pages(temp_pdf_path)

            merged = merge_questions_with_marks(detected["questions"], marks_map)
            editable_rows = []
            for row in merged:
                editable_rows.append(
                    {
                        "question_id": row["question_id"],
                        "pages": ",".join(str(x) for x in row["pages"]),
                        "obtained_marks": int(row["obtained_marks"]),
                    }
                )
            st.session_state.editable_df = pd.DataFrame(editable_rows)
            st.session_state.document_id = document_id
            st.session_state.total_pages = total_pages
            st.success("Auto detection complete. You can edit the table before export.")
        except Exception as exc:
            st.error(f"Error: {exc}")
        finally:
            if "temp_pdf_path" in locals() and os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

if not st.session_state.editable_df.empty:
    st.subheader("Edit Detected Mapping")
    edited_df = st.data_editor(
        st.session_state.editable_df,
        num_rows="dynamic",
        use_container_width=True,
        key="questions_editor",
    )
    st.session_state.editable_df = edited_df

    if st.button("Generate JSON"):
        try:
            validation_errors = _validate_questions_for_export(st.session_state.editable_df)
            if validation_errors:
                st.error("Cannot generate JSON. Please fix page values for these questions:")
                st.write(", ".join(validation_errors))
                st.stop()

            questions = []
            for _, row in st.session_state.editable_df.iterrows():
                question_id = str(row["question_id"]).strip()
                if not question_id:
                    continue
                pages = parse_pages_value(row["pages"])
                obtained_marks = int(row["obtained_marks"])
                questions.append(
                    {
                        "question_id": question_id,
                        "pages": pages,
                        "obtained_marks": obtained_marks,
                    }
                )

            payload = build_output_json(
                document_id=st.session_state.document_id,
                total_pages=st.session_state.total_pages,
                questions=questions,
            )
            output_dir = Path("data/output")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{st.session_state.document_id}.json"
            save_output_json(payload, str(output_path))

            st.success(f"JSON generated: {output_path}")
            st.json(payload)
        except Exception as exc:
            st.error(f"Error while generating JSON: {exc}")
