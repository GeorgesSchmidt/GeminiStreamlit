import os
import cv2
import numpy as np
import langid
import easyocr
import fitz  # PyMuPDF
import warnings
import streamlit as st

# --- Désactivation des warnings et réglages PyTorch ---
warnings.filterwarnings("ignore")
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# --- CHARGEMENT OPTIMISÉ DU MODÈLE (C'est la clé !) ---
@st.cache_resource
def load_ocr_reader():
    """
    Charge le modèle une seule fois pour tout le cycle de vie de l'app.
    On charge 'fr' et 'en' par défaut pour couvrir la majorité des cas sans saturer la RAM.
    """
    return easyocr.Reader(['fr', 'en'], gpu=False)

class ReadPDF:
    def __init__(self):
        self.pages = []      
        self.text = ""       
        self.lang = "fr"     
        self.dpi = 150  # Réduit de 180 à 150 pour économiser 30% de RAM

    def convert_pdf(self, uploaded_file):
        """Convertit le PDF en images avec gestion propre de la mémoire."""
        try:
            # Important : on lit le stream directement
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            self.pages = []

            for page in doc:
                pix = page.get_pixmap(dpi=self.dpi)
                # Conversion directe en Gris pour économiser la mémoire
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                
                if pix.n >= 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                
                img = cv2.equalizeHist(img)
                self.pages.append(img)
                
            doc.close() # Libère le fichier PDF
            print(f"[INFO] PDF chargé : {len(self.pages)} pages")
        except Exception as e:
            st.error(f"Erreur de conversion PDF : {e}")

    def read_doc(self):
        """Exécute l'OCR en utilisant le reader en cache."""
        try:
            if not self.pages:
                return "Aucune page à lire."

            # Utilise le modèle partagé (évite de recréer un objet Reader)
            reader = load_ocr_reader()
            
            extracted_pages = []
            
            # Barre de progression Streamlit pour voir l'avancement
            progress_bar = st.progress(0)
            
            for i, page_np in enumerate(self.pages):
                # OCR sur la page
                page_blocks = reader.readtext(page_np, detail=0, paragraph=True)
                page_text = " ".join(page_blocks)
                extracted_pages.append(page_text)
                
                # Mise à jour de la progression
                progress_bar.progress((i + 1) / len(self.pages))
            
            self.text = "\n\n".join(extracted_pages)
            
            # OPTIONNEL : Détection de langue après coup sur le texte extrait
            if self.text.strip():
                self.lang, _ = langid.classify(self.text[:500]) # Sur les 500 premiers caractères
                
            return self.text

        except Exception as e:
            st.error(f"Erreur OCR : {e}")
            return ""

# --- Exemple d'intégration dans ton mainStreamlit.py ---
def run_app():
    st.title("OCR PDF / Image")
    
    file = st.file_uploader("Chargez votre document", type=["pdf", "png", "jpg"])
    
    if file:
        if st.button("Lancer l'extraction"):
            with st.spinner("Traitement en cours..."):
                reader_obj = ReadPDF()
                
                # Selon le type de fichier
                if file.type == "application/pdf":
                    reader_obj.convert_pdf(file)
                else:
                    # Pour les images, utilise ton ancienne méthode convert_img 
                    # mais avec cv2.IMREAD_GRAYSCALE directement
                    file_bytes = np.frombuffer(file.read(), np.uint8)
                    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                    reader_obj.pages = [cv2.equalizeHist(img)]
                
                resultat = reader_obj.read_doc()
                st.success("Extraction terminée !")
                st.text_area("Texte extrait", resultat, height=300)

if __name__ == "__main__":
    run_app()