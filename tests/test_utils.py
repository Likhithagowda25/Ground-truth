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

if __name__ == "__main__":
    unittest.main()
