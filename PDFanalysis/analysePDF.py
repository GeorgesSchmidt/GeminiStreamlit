import os
import cv2
import numpy as np
import langid
import easyocr
import fitz  # PyMuPDF
import warnings

# --- Disable warnings ---
warnings.filterwarnings("ignore")

# --- Environment settings for PyTorch / EasyOCR ---
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = ""


warnings.filterwarnings("ignore")

class ReadPDF:
    """
    Class handling:
    - Reading images or PDF files
    - Detecting language from sample OCR
    - Extracting text from all pages using OCR
    """

    def __init__(self):
        self.pages = []      # List of pages (numpy arrays, grayscale)
        self.text = ""       # Final extracted text
        self.lang = "en"     # Default fallback language
        self.dpi = 180

        self.supported_langs = ['en', 'fr', 'de', 'es', 'it']
        self.readers = {}
        # Multi-language OCR reader (used only for language detection)
        self.reader_all = easyocr.Reader(
            self.supported_langs,
            gpu=False
        )

    # -----------------------------------------------------------
    # Load image
    # -----------------------------------------------------------
    def convert_img(self, uploaded_file):
        """Convert an uploaded image file to a numpy array and prepare it for OCR."""
        try:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

            if img is None:
                raise ValueError("Image decoding error")

            # Improve OCR quality with histogram equalization
            img = cv2.equalizeHist(img)

            print(f"[INFO] Image imported, shape = {img.shape}")
            self.pages = [img]

        except Exception as e:
            print(f"[ERROR] Failed to convert image: {e}")

    # -----------------------------------------------------------
    # Load PDF
    # -----------------------------------------------------------
    def convert_pdf(self, uploaded_file):
        """Convert PDF bytes into a list of grayscale numpy images using PyMuPDF."""
        try:
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            self.pages = []

            for i, page in enumerate(doc):
                # Render page to image
                pix = page.get_pixmap(dpi=self.dpi)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

                # Convert RGB/RGBA to grayscale
                if pix.n >= 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                # Histogram equalization to improve OCR
                img = cv2.equalizeHist(img)
                self.pages.append(img)

            print(f"[INFO] PDF loaded with {len(self.pages)} page(s) using PyMuPDF")

        except Exception as e:
            print(f"[ERROR] Failed to convert PDF: {e}")

    # -----------------------------------------------------------
    # Language detection
    # -----------------------------------------------------------
    def detect_language(self):
        """Detect the language of the text using OCR on a sample (first page)."""
        try:
            if not self.pages:
                print("[WARNING] No pages loaded for language detection")
                return

            sample_img = self.pages[0]
            sample_text = " ".join(self.reader_all.readtext(sample_img, detail=0, paragraph=True))

            if not sample_text.strip():
                print("[WARNING] No text detected in sample for language detection")
                return

            self.lang, prob = langid.classify(sample_text)
            print(f"[INFO] Language detected: {self.lang} (confidence {prob:.2f})")

        except Exception as e:
            print(f"[ERROR] Language detection failed: {e}")

    # --------------------------------------------------
    # Reader OCR (cache)
    # --------------------------------------------------
    def _get_reader(self):
        if self.lang not in self.readers:
            self.readers[self.lang] = easyocr.Reader(
                [self.lang],
                gpu=False
            )
        return self.readers[self.lang]
    # -----------------------------------------------------------
    # Full OCR
    # -----------------------------------------------------------
    def read_doc(self, max_pages_per_chunk=3):
        """Perform OCR on the document using the detected language, chunked if needed."""
        try:
            if not self.pages:
                print("[ERROR] No pages available for OCR")
                return

            #reader_final = easyocr.Reader([self.lang])
            reader_final = self._get_reader()
            self.text = ""

            # Diviser en chunks
            for start in range(0, len(self.pages), max_pages_per_chunk):
                chunk_pages = self.pages[start:start+max_pages_per_chunk]
                for i, page_np in enumerate(chunk_pages):
                    page_blocks = reader_final.readtext(page_np, detail=0, paragraph=True)
                    page_text = " ".join(page_blocks)
                    self.text += page_text + "\n"
                    print(f"[INFO] Page {start+i+1} processed, {len(page_blocks)} text blocks")

            if self.text.strip():
                print(f"[INFO] OCR completed, total text length = {len(self.text)} characters")
            else:
                print("[WARNING] OCR completed but no text was detected.")

        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")

# -----------------------------------------------------------
# Standalone test mode
# -----------------------------------------------------------
def main(path):
    """Standalone testing (for development only)."""
    reader = ReadPDF()

    ext = path.lower().split('.')[-1]

    if ext in ['png', 'jpg', 'jpeg']:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img = cv2.equalizeHist(img)
        reader.pages.append(img)

    elif ext == "pdf":
        with open(path, "rb") as f:
            reader.convert_pdf(f)

    else:
        print("Unsupported file")
        return

    reader.detect_language()
    reader.read_doc(max_pages=5)
    print(reader.text)


if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'PDF', 'attestation_covid.pdf')
    test_path = "/path/to/your/file.pdf"
    main(path)
