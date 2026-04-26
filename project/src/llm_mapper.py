import json
import os
from typing import Any, Dict, List

import fitz
import google.generativeai as genai


LLM_PROMPT_TEMPLATE = """You are given a student's answer script.

Identify all questions and the page numbers where they appear.

Rules:

- Use page numbers starting from 1
- Question IDs must be like Q1a, Q2b
- Return ONLY JSON in this format:
{{
  "questions": [
    {{"question_id": "Q1a", "pages": [1,2]}},
    {{"question_id": "Q1b", "pages": [3]}}
  ]
}}

Content:
{pdf_text}
"""


def _extract_pdf_text_with_pages(pdf_path: str) -> str:
    page_blocks = []
    doc = fitz.open(pdf_path)
    try:
        for i, page in enumerate(doc, start=1):
            page_text = page.get_text().strip()
            page_blocks.append(f"[Page {i}]\n{page_text}")
    finally:
        doc.close()
    return "\n\n".join(page_blocks)


def _extract_json(raw_text: str) -> Dict[str, Any]:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("LLM response is not valid JSON.")
        return json.loads(raw_text[start : end + 1])


def _normalize_model_name(model_name: str) -> str:
    return model_name.replace("models/", "", 1) if model_name.startswith("models/") else model_name


def _configure_gemini_api() -> None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable.")
    genai.configure(api_key=api_key)


def detect_questions_from_pdf(pdf_text: str, model_name: str = "gemini-2.5-pro") -> str:
    _configure_gemini_api()
    resolved_model = _normalize_model_name(model_name)
    model = genai.GenerativeModel(resolved_model)
    prompt = LLM_PROMPT_TEMPLATE.format(pdf_text=pdf_text)
    try:
        response = model.generate_content(prompt)
    except Exception as exc:
        raise ValueError(f"Gemini request failed with model '{resolved_model}': {exc}") from exc
    if not getattr(response, "text", None):
        raise ValueError("Gemini returned an empty response.")
    return response.text


def detect_question_pages(pdf_path: str, model: str = "gemini-2.5-pro") -> Dict[str, Any]:
    pdf_text = _extract_pdf_text_with_pages(pdf_path)
    if not pdf_text.strip():
        raise ValueError("No readable text found in PDF.")

    text_output = detect_questions_from_pdf(pdf_text, model_name=model)
    parsed = _extract_json(text_output)

    if "questions" not in parsed or not isinstance(parsed["questions"], list):
        raise ValueError("LLM JSON missing 'questions' list.")

    return parsed
