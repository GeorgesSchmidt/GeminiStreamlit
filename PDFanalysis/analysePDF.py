import os
import cv2
import numpy as np
import langid
import easyocr
from pdf2image import convert_from_bytes
import warnings

# --- Disable warnings ---
warnings.filterwarnings("ignore")

# --- Environment settings for PyTorch / EasyOCR ---
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"


class ReadPDF:
    """
    Class handling:
    - Reading images or PDF files
    - Detecting language from sample OCR
    - Extracting text from all pages using OCR
    """

    def __init__(self):
        self.pages = []      # List of pages (numpy arrays or PIL images)
        self.text = ""       # Final extracted text
        self.lang = "en"     # Default fallback language

        # Multi-language OCR reader (used only for language detection)
        self.reader_all = easyocr.Reader(['en', 'fr', 'de', 'es', 'it'])

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
        """Convert PDF bytes into a list of images."""
        try:
            self.pages = convert_from_bytes(uploaded_file.read(), dpi=300)
            print(f"[INFO] PDF loaded with {len(self.pages)} page(s)")
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

            # Convert PIL image to numpy if needed
            sample_img = np.array(self.pages[0])

            sample_text = " ".join(self.reader_all.readtext(sample_img, detail=0))

            if not sample_text.strip():
                print("[WARNING] No text detected in sample for language detection")
                return

            self.lang, prob = langid.classify(sample_text)
            print(f"[INFO] Language detected: {self.lang} (confidence {prob:.2f})")

        except Exception as e:
            print(f"[ERROR] Language detection failed: {e}")

    # -----------------------------------------------------------
    # Full OCR
    # -----------------------------------------------------------
    def read_doc(self, max_pages=3):
        """Perform OCR on the document using the detected language."""
        try:
            if not self.pages:
                print("[ERROR] No pages available for OCR")
                return

            reader_final = easyocr.Reader([self.lang])
            self.text = ""

            for i, page in enumerate(self.pages[:max_pages]):
                page_np = np.array(page)
                page_blocks = reader_final.readtext(page_np, detail=0)
                page_text = " ".join(page_blocks)

                self.text += page_text + "\n"

                print(f"[INFO] Page {i + 1} processed, {len(page_blocks)} text blocks")

            print(f"[INFO] OCR completed, text length = {len(self.text)} characters")

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
    reader.read_doc()
    print(reader.text)


if __name__ == '__main__':
    test_path = "/path/yourfile.png"
    main(test_path)
