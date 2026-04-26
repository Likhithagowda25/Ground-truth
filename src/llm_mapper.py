import json
import os
from typing import Any, Dict, List

import fitz
import vertexai
from vertexai.generative_models import GenerativeModel, Part


LLM_PROMPT_TEMPLATE = """You are an expert at analyzing student answer scripts.
I am providing you with a PDF of a student's handwritten answer script.
Your task is to identify the exact page numbers where each of the following questions are answered.

Expected Question IDs: {question_ids}

Rules:
- Use page numbers starting from 1.
- If a question spans multiple pages, list all of them: [1, 2].
- Return ONLY a valid JSON object.
- Use the exact Question IDs provided above.

Format:
{{
  "questions": [
    {{"question_id": "1a", "pages": [1, 2]}},
    {{"question_id": "1b", "pages": [3]}}
  ]
}}
"""


def _extract_json(raw_text: str) -> Dict[str, Any]:
    raw_text = raw_text.strip()
    # Remove markdown code blocks if present
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if lines[0].startswith("```json"):
            raw_text = "\n".join(lines[1:-1])
        elif lines[0].startswith("```"):
            raw_text = "\n".join(lines[1:-1])
            
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"LLM response is not valid JSON: {raw_text}")
        return json.loads(raw_text[start : end + 1])


def _init_vertexai():
    # Vertex AI will use the project ID from gcloud environment if not explicitly provided
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    vertexai.init(project=project_id, location=location)


def detect_questions_from_pdf(pdf_path: str, question_ids: list, model_name: str = "gemini-2.5-pro") -> str:
    _init_vertexai()
    model = GenerativeModel(model_name)
    
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    
    pdf_part = Part.from_data(data=pdf_data, mime_type="application/pdf")
    prompt = LLM_PROMPT_TEMPLATE.format(question_ids=", ".join(question_ids))
    
    try:
        response = model.generate_content([pdf_part, prompt])
    except Exception as exc:
        raise ValueError(f"Vertex AI request failed: {exc}") from exc
        
    if not response.text:
        raise ValueError("Vertex AI returned an empty response.")
    return response.text


def detect_question_pages(pdf_path: str, question_ids: list, model: str = "gemini-2.5-pro") -> Dict[str, Any]:
    text_output = detect_questions_from_pdf(pdf_path, question_ids, model_name=model)
    parsed = _extract_json(text_output)

    if "questions" not in parsed or not isinstance(parsed["questions"], list):
        raise ValueError("LLM JSON missing 'questions' list.")

    return parsed
