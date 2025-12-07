import sys
import os
import warnings

# ----------------------------
# Supprimer les warnings
# ----------------------------
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", module="torch|easyocr")

# ----------------------------
# Import du module à tester
# ----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import pytest
import cv2
import numpy as np
from unittest.mock import patch
from PDFanalysis.analysePDF import ReadPDF

# ----------------------------
# Helper : PDF factice
# ----------------------------
def generate_fake_pdf_bytes():
    """Retourne un PDF factice en mémoire"""
    return io.BytesIO(b"%PDF-1.4 fake pdf content")

# ----------------------------
# Test : convert_img
# ----------------------------
def test_convert_img():
    reader = ReadPDF()
    img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    _, buffer = cv2.imencode(".png", img)
    fake_file = io.BytesIO(buffer.tobytes())
    fake_file.name = "test.png"
    reader.convert_img(fake_file)

    assert len(reader.pages) == 1
    assert isinstance(reader.pages[0], np.ndarray)
    assert reader.pages[0].ndim == 2

# ----------------------------
# Test : convert_pdf (mocké)
# ----------------------------
@patch("PDFanalysis.analysePDF.convert_from_bytes")
def test_convert_pdf(mock_convert):
    mock_convert.return_value = [np.random.randint(0, 256, (100,100), dtype=np.uint8)]
    reader = ReadPDF()
    pdf_buffer = generate_fake_pdf_bytes()
    reader.convert_pdf(pdf_buffer)

    assert len(reader.pages) == 1

# ----------------------------
# Test : language detection
# ----------------------------
def test_detect_language_with_text_image():
    reader = ReadPDF()
    img = np.ones((100, 100), dtype=np.uint8)
    reader.pages = [img]

    with patch.object(reader, "reader_all", create=True) as mock_reader:
        mock_reader.readtext = lambda x, detail: ["Hello world"]
        reader.detect_language()
        assert reader.lang in ["fr", "en", "de", "es", "it"]

# ----------------------------
# Test : OCR read_doc
# ----------------------------
def test_read_doc_with_mocked_ocr():
    reader = ReadPDF()
    img = np.ones((100, 100), dtype=np.uint8)
    reader.pages = [img]
    reader.lang = "en"

    with patch("easyocr.Reader.readtext", return_value=["Test OCR"]):
        reader.read_doc()

    assert isinstance(reader.text, str)
    assert "Test OCR" in reader.text

# ----------------------------
# Test : full pipeline
# ----------------------------
def test_full_pipeline_with_mocked_pdf():
    reader = ReadPDF()

    # Mock convert_from_bytes pour PDF
    with patch("PDFanalysis.analysePDF.convert_from_bytes", return_value=[np.ones((100,100), dtype=np.uint8)]):
        reader.convert_pdf(generate_fake_pdf_bytes())

    # Mock EasyOCR pour language detection
    with patch.object(reader, "reader_all", create=True) as mock_reader:
        mock_reader.readtext = lambda x, detail: ["Bonjour"]
        reader.detect_language()
        assert reader.lang in ["fr", "en", "de", "es", "it"]

    # Mock EasyOCR pour read_doc
    with patch("easyocr.Reader.readtext", return_value=["Bonjour"]):
        reader.read_doc()

    assert reader.lang != ""
    assert len(reader.pages) == 1
    assert "Bonjour" in reader.text
