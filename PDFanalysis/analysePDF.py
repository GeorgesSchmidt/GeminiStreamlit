import os
import sys
import cv2
import numpy as np
import langid
import easyocr
from pdf2image import convert_from_path
import warnings
warnings.filterwarnings("ignore")
os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"

class ReadPDF:
    def __init__(self):
        self.reader_all = easyocr.Reader(['en', 'fr', 'de', 'es'])
        
    def convert_img(self, uploaded_file):
        self.pages = []
        print('Nom du fichier:', uploaded_file.name)

        # Lire le fichier en mémoire
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)

        # Décoder l'image en niveau de gris
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

        # Vérifier si l'image est correctement lue
        if img is None:
            print("Erreur : impossible de lire l'image")
            return

        # Equalisation de l'histogramme
        img_eq = cv2.equalizeHist(img)

        print('Shape de l\'image:', img_eq.shape)

        # Ajouter l'image traitée à la liste
        self.pages.append(img_eq)
        
    def detect_type(self, path):
        type_doc = path.split('.')[-1]
        if type_doc == 'pdf':
            self.pages = convert_from_path(path, dpi=300)
            print('number of pages', len(self.pages))
        elif type_doc == 'jpeg' or type_doc == 'png':
            self.pages = []
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img = cv2.equalizeHist(img)
            self.pages.append(img)
            
        
    def detect_language(self):
        sample_img = np.array(self.pages[0])
        
        sample_text = " ".join(self.reader_all.readtext(sample_img, detail=0))
        
        # Détection de la langue
        self.lang, prob = langid.classify(sample_text)
        print(f"detected language = {self.lang}")
        
    def read_doc(self):
        # OCR complet avec la langue détectée
        reader_final = easyocr.Reader([self.lang])
        self.text = ""
        for i, page in enumerate(self.pages[:3]):
            page_text_blocks = reader_final.readtext(np.array(page), detail=0)
            page_text = " ".join(page_text_blocks)
            self.text += page_text + "\n"
            print(f"Page {i+1} traitée, {len(page_text_blocks)} blocs détectés")
        
        print('text length', len(self.text))
    

def main(path):
    analys = ReadPDF()
    analys.detect_type(path)
    analys.detect_language()
    analys.read_doc()
        
if __name__=='__main__':
    path_pdf = '/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/PDF/BusinessPlanV2.pdf'
    path_img = '/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/Pics/text_img.png'
    main(path=path_img)
    