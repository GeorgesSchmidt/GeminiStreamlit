import io
import numpy as np
import pytest
from unittest.mock import patch

from PDFanalysis.analysePDF import ReadPDF


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def disable_easyocr_init(monkeypatch):
    """Disable EasyOCR heavy initialization"""
    monkeypatch.setattr("easyocr.Reader.__init__", lambda self, *a, **k: None)


@pytest.fixture
def fake_pdf_bytes():
    return io.BytesIO(b"%PDF-1.4 fake pdf content")


@pytest.fixture
def fake_pixmap():
    class FakePix:
        width = 100
        height = 100
        n = 1
        samples = np.ones((100 * 100,), dtype=np.uint8)

    return FakePix()


@pytest.fixture
def fake_pdf_page(fake_pixmap):
    class FakePage:
        def get_pixmap(self, dpi=300):
            return fake_pixmap

    return FakePage()


@pytest.fixture
def reader():
    return ReadPDF()


# ============================================================
# Tests
# ============================================================

def test_convert_img(reader):
    img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)

    import cv2
    _, buffer = cv2.imencode(".png", img)

    fake_file = io.BytesIO(buffer.tobytes())
    fake_file.name = "test.png"

    reader.convert_img(fake_file)

    assert len(reader.pages) == 1
    assert reader.pages[0].shape == (100, 100)


@patch("PDFanalysis.analysePDF.fitz.open")
def test_convert_pdf(mock_fitz_open, reader, fake_pdf_bytes, fake_pdf_page):
    mock_fitz_open.return_value = [fake_pdf_page]

    reader.convert_pdf(fake_pdf_bytes)

    assert len(reader.pages) == 1
    assert isinstance(reader.pages[0], np.ndarray)


def test_detect_language(reader):
    reader.pages = [np.ones((100, 100), dtype=np.uint8)]

    with patch.object(reader.reader_all, "readtext", return_value=["Bonjour le monde"]):
        reader.detect_language()

    assert reader.lang in ["fr", "en", "de", "es", "it"]


def test_read_doc(reader):
    reader.pages = [np.ones((100, 100), dtype=np.uint8)]
    reader.lang = "en"

    with patch("easyocr.Reader.readtext", return_value=["Hello", "world"]):
        reader.read_doc()

    assert "Hello world" in reader.text


def test_full_pipeline(reader, fake_pdf_bytes, fake_pdf_page):
    with patch("PDFanalysis.analysePDF.fitz.open", return_value=[fake_pdf_page]):
        reader.convert_pdf(fake_pdf_bytes)

    with patch.object(reader.reader_all, "readtext", return_value=["Bonjour"]):
        reader.detect_language()

    with patch("easyocr.Reader.readtext", return_value=["Bonjour"]):
        reader.read_doc()

    assert len(reader.pages) == 1
    assert reader.text.strip() != ""
    assert reader.lang != ""
