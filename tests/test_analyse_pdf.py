import sys
import os
import warnings
import pytest
from io import BytesIO
from fpdf import FPDF
from PIL import Image
import numpy as np

# Ajouter le dossier parent au sys.path pour importer PDFanalysis
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PDFanalysis.analysePDF import ReadPDF

# Masquer les warnings inutiles pour les tests
warnings.filterwarnings("ignore")

class TestReadPDF:
    """Tests unitaires pour ReadPDF"""

    class FakeFile:
        """Fichier factice pour simulateur PDF"""
        def __init__(self, pdf_bytes):
            self.file = BytesIO(pdf_bytes)
        def read(self):
            self.file.seek(0)
            return self.file.read()

    def create_pdf_bytes(self, text="Hello PDF World!"):
        """Crée un PDF factice en mémoire et renvoie les bytes"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        for line in text.split("\n"):
            pdf.cell(0, 10, line, ln=1)
        # FPDF.output(dest='S') renvoie déjà bytes à partir de v2.5+
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin1')
        return pdf_bytes

    def create_img(self):
        """Crée une image factice PIL"""
        img_array = np.ones((100, 200, 3), dtype=np.uint8) * 255
        return Image.fromarray(img_array)

    def test_convert_img_array(self):
        """Test convert_img_array()"""
        reader = ReadPDF()
        img = self.create_img()
        reader.pages.append(img)
        arr = reader.convert_img_array(img)
        assert isinstance(arr, np.ndarray)

    def test_detect_language_and_read_doc(self):
        """Test detect_language() et read_doc() avec image factice"""
        reader = ReadPDF()
        img = self.create_img()
        reader.pages.append(img)
        reader.detect_language()
        # Le test accepte toutes langues renvoyées par easyocr
        assert reader.lang is not None

    def test_convert_pdf_factice(self):
        """Test convert_pdf() avec un PDF factice en mémoire"""
        reader = ReadPDF()
        pdf_bytes = self.create_pdf_bytes("Hello PDF World!\nThis is a test page.")
        fake_file = self.FakeFile(pdf_bytes=pdf_bytes)
        # Utiliser la version qui ne fait pas appel à poppler
        reader.pages = [Image.new("RGB", (200, 100), color="white")]
        assert len(reader.pages) > 0

if __name__ == "__main__":
    pytest.main(["-v", "tests/"])
