import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys

# Add src to sys.path to import llm_mapper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from llm_mapper import detect_questions_from_pdf, detect_question_pages

class TestLLMMapper(unittest.TestCase):

    @patch("llm_mapper.GenerativeModel")
    @patch("llm_mapper.vertexai.init")
    @patch("llm_mapper.Part")
    def test_detect_questions_from_pdf(self, mock_part, mock_init, mock_gen_model):
        mock_model_instance = mock_gen_model.return_value
        mock_response = MagicMock()
        mock_response.text = '{"questions": [{"question_id": "1a", "pages": [1]}]}'
        mock_model_instance.generate_content.return_value = mock_response

        # Mock Part.from_data
        mock_part.from_data.return_value = MagicMock()

        with patch("builtins.open", mock_open(read_data=b"fake pdf content")):
            pdf_path = "fake.pdf"
            question_ids = ["1a"]
            result = detect_questions_from_pdf(pdf_path, question_ids)

        self.assertEqual(result, mock_response.text)
        mock_gen_model.assert_called_with("gemini-2.5-pro")
        mock_model_instance.generate_content.assert_called()
        mock_part.from_data.assert_called_once()

    @patch("llm_mapper.detect_questions_from_pdf")
    def test_detect_question_pages(self, mock_detect):
        mock_detect.return_value = '{"questions": [{"question_id": "1a", "pages": [1]}]}'
        
        pdf_path = "fake.pdf"
        question_ids = ["1a"]
        result = detect_question_pages(pdf_path, question_ids)

        self.assertEqual(result["questions"][0]["question_id"], "1a")
        self.assertEqual(result["questions"][0]["pages"], [1])

if __name__ == "__main__":
    unittest.main()
