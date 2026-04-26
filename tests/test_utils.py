import unittest
import os
from src.utils import render_pdf_page

class TestUtils(unittest.TestCase):
    def test_render_pdf_page(self):
        pdf_path = "data/scripts/ds_001.pdf"
        if not os.path.exists(pdf_path):
            self.skipTest(f"Sample PDF {pdf_path} not found")
        
        # Test rendering page 1
        image_bytes = render_pdf_page(pdf_path, 1)
        self.assertIsInstance(image_bytes, bytes)
        self.assertTrue(len(image_bytes) > 0)
        # PNG signature
        self.assertEqual(image_bytes[:8], b'\x89PNG\r\n\x1a\n')

    def test_render_pdf_page_invalid_number(self):
        pdf_path = "data/scripts/ds_001.pdf"
        if not os.path.exists(pdf_path):
            self.skipTest(f"Sample PDF {pdf_path} not found")
        
        # Test zero (invalid for 1-indexed)
        with self.assertRaises(ValueError) as cm:
            render_pdf_page(pdf_path, 0)
        self.assertIn("Invalid page number 0", str(cm.exception))
        
        # Test out of bounds
        with self.assertRaises(ValueError) as cm:
            render_pdf_page(pdf_path, 999)
        self.assertIn("Invalid page number 999", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
