import os
import cv2
import numpy as np
import langid
import easyocr
import fitz  # PyMuPDF
import warnings
import streamlit as st

# --- Disable warnings and PyTorch settings ---
warnings.filterwarnings("ignore")
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# --- OPTIMIZED MODEL LOADING ---
@st.cache_resource
def load_ocr_reader():
    """
    Loads the model once for the entire app lifecycle.
    We load 'en' and 'fr' by default to save RAM.
    """
    return easyocr.Reader(['en', 'fr'], gpu=False)

class ReadPDF:
    def __init__(self):
        self.pages = []      # List of images (numpy arrays)
        self.text = ""       # Extracted text
        self.lang = "en"     # Default language
        self.dpi = 150       # Reduced DPI to save 30% RAM compared to 180

    def convert_img(self, uploaded_file):
        """
        Convert an uploaded image file (jpg, png) to a grayscale numpy array.
        This was the missing method causing the AttributeError.
        """
        try:
            file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                raise ValueError("Could not decode image.")

            # Improve contrast for better OCR
            img = cv2.equalizeHist(img)
            self.pages = [img]
            print(f"[INFO] Image loaded successfully.")
        except Exception as e:
            st.error(f"Image conversion error: {e}")

    def convert_pdf(self, uploaded_file):
        """Convert PDF pages into grayscale images with memory management."""
        try:
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            self.pages = []

            for page in doc:
                pix = page.get_pixmap(dpi=self.dpi)
                # Direct conversion to grayscale to save memory
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                
                if pix.n >= 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                
                img = cv2.equalizeHist(img)
                self.pages.append(img)
                
            doc.close() # Free PDF file from memory
            print(f"[INFO] PDF loaded: {len(self.pages)} pages")
        except Exception as e:
            st.error(f"PDF conversion error: {e}")

    def detect_language(self):
        """
        Optional: Detect language based on the first page content.
        Can be called manually or inside read_doc.
        """
        if not self.pages:
            return
        try:
            reader = load_ocr_reader()
            sample_results = reader.readtext(self.pages[0], detail=0, paragraph=True)
            sample_text = " ".join(sample_results)
            if sample_text.strip():
                self.lang, _ = langid.classify(sample_text)
        except Exception:
            self.lang = "en"

    def read_doc(self):
        """Perform OCR on all pages using the cached reader."""
        try:
            if not self.pages:
                return "No content to read."

            # Use the shared model from cache
            reader = load_ocr_reader()
            
            extracted_pages = []
            
            # Progress bar for the user
            progress_bar = st.progress(0)
            
            for i, page_np in enumerate(self.pages):
                # Run OCR
                page_blocks = reader.readtext(page_np, detail=0, paragraph=True)
                page_text = " ".join(page_blocks)
                extracted_pages.append(page_text)
                
                # Update progress
                progress_bar.progress((i + 1) / len(self.pages))
            
            self.text = "\n\n".join(extracted_pages)
            
            # Detect language after extraction
            if self.text.strip():
                self.lang, _ = langid.classify(self.text[:500])
                
            return self.text

        except Exception as e:
            st.error(f"OCR process failed: {e}")
            return ""

# This part is only for local testing, Streamlit uses the class above.
if __name__ == "__main__":
    print("Class ReadPDF is ready for use in Streamlit.")