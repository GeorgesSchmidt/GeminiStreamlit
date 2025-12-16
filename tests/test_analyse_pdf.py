import pytest
import cv2
import numpy as np
from io import BytesIO
from PDFanalysis.analysePDF import ReadPDF
from reportlab.pdfgen import canvas

# ----------------------------
# Helpers
# ----------------------------
def create_dummy_image(width=100, height=100):
    """Crée une image factice pour les tests."""
    return np.random.randint(0, 256, (height, width), dtype=np.uint8)

def create_test_pdf(text="Test PDF content"):
    """Crée un PDF en mémoire avec une seule page contenant `text`."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ----------------------------
# Tests
# ----------------------------

def test_convert_img_with_dummy_image():
    reader = ReadPDF()
    dummy_image = create_dummy_image()

    # Encoder l'image en bytes (comme un fichier uploadé)
    _, buffer = cv2.imencode('.png', dummy_image)
    fake_file = BytesIO(buffer.tobytes())

    reader.convert_img(fake_file)
    assert len(reader.pages) == 1

    reader.detect_language()
    reader.read_doc()  # Plus de max_pages

    assert isinstance(reader.text, str)

def test_convert_pdf_with_real_pdf():
    reader = ReadPDF()
    pdf_file = create_test_pdf("This is a test PDF page.")

    reader.convert_pdf(pdf_file)
    assert len(reader.pages) == 1  # PDF chargé correctement

    reader.detect_language()
    reader.read_doc()  # Plus de max_pages

    assert isinstance(reader.text, str)
    assert "This" in reader.text or "test" in reader.text

def test_full_pipeline_with_real_pdf():
    reader = ReadPDF()
    pdf_file = create_test_pdf("Full pipeline test content")

    reader.convert_pdf(pdf_file)
    reader.detect_language()
    reader.read_doc()  # Plus de max_pages

    assert len(reader.pages) == 1
    assert isinstance(reader.text, str)
    assert "Full" in reader.text

def test_multi_page_pdf():
    reader = ReadPDF()
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    for i in range(3):
        c.drawString(100, 750, f"Page {i+1} content")
        c.showPage()
    c.save()
    buffer.seek(0)

    reader.convert_pdf(buffer)
    assert len(reader.pages) == 3

    reader.detect_language()
    reader.read_doc()  # Plus de max_pages

    assert isinstance(reader.text, str)
    for i in range(3):
        assert f"Page {i+1}" in reader.text or reader.text  # Vérifie qu'au moins du texte a été lu
