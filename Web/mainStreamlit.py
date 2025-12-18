import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from google import genai

# --- Chargement des variables d'environnement ---
load_dotenv()

# --- Import du module personnalisé ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PDFanalysis.analysePDF import ReadPDF

class Main:
    def __init__(self):
        self._init_gemini_client()
        # Initialisation de l'objet OCR
        if "analyse_file" not in st.session_state:
            st.session_state.analyse_file = ReadPDF()
        
        # Stockage du texte extrait pour éviter de relancer l'OCR inutilement
        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = None
            st.session_state.detected_lang = "Inconnue"

    def _init_gemini_client(self):
        """Initialisation sécurisée du client Gemini."""
        # Utilise st.secrets pour la prod, os.getenv pour le local
        api_key = st.secrets.get("GOOGLE_API_KEY_Gem") or os.getenv("GOOGLE_API_KEY_Gem")

        if not api_key:
            st.error("❌ Erreur : Clé API manquante (GOOGLE_API_KEY_Gem).")
            st.stop()

        if "client" not in st.session_state:
            st.session_state.client = genai.Client(api_key=api_key)

        if "chat" not in st.session_state:
            # Correction du modèle (gemini-2.0-flash est le nom actuel standard)
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.0-flash" 
            )

    def run_ocr_process(self, uploaded_file):
        """Exécute l'OCR et stocke le résultat dans le session_state."""
        start_time = time.time()
        extension = uploaded_file.name.split('.')[-1].lower()
        
        reader = st.session_state.analyse_file

        with st.spinner("🔍 OCR en cours... Merci de patienter."):
            if extension in ['png', 'jpg', 'jpeg']:
                reader.convert_img(uploaded_file)
            elif extension == "pdf":
                reader.convert_pdf(uploaded_file)
            
            # Vérification de la présence de la méthode avant appel
            if hasattr(reader, 'detect_language'):
                reader.detect_language()
            
            reader.read_doc()
            
            # Sauvegarde dans le state
            st.session_state.extracted_text = reader.text
            st.session_state.detected_lang = reader.lang
            st.session_state.duration = int(time.time() - start_time)

    def run(self):
        st.title("📘 Gemini Image/Text Analyzer")
        st.info("L'OCR prend environ 30s par page. Merci de patienter après l'upload.")

        uploaded_file = st.file_uploader("📤 Upload an image or PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

        if uploaded_file:
            # Si un nouveau fichier est chargé, on reset l'ancien texte
            if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
                st.session_state.last_uploaded = uploaded_file.name
                st.session_state.extracted_text = None

            # Bouton pour lancer l'OCR
            if st.session_state.extracted_text is None:
                if st.button("🚀 Lancer l'extraction de texte"):
                    self.run_ocr_process(uploaded_file)
                    st.rerun()

            # Si le texte a été extrait, on affiche les résultats et Gemini
            if st.session_state.extracted_text:
                st.subheader("📝 Texte Extrait :")
                st.text_area("Résultat :", st.session_state.extracted_text, height=250)
                
                col1, col2 = st.columns(2)
                col1.write(f"⏱ Durée : {st.session_state.get('duration', 0)}s")
                col2.write(f"🌍 Langue : {st.session_state.detected_lang}")

                st.divider()

                # Interaction Gemini
                st.subheader("🤖 Question à Gemini")
                user_question = st.text_input("Posez une question sur le document :", key="gemini_q")
                
                if st.button("🔍 Demander à Gemini"):
                    if not user_question:
                        user_question = "Fais un résumé synthétique de ce texte."
                    
                    prompt = f"Texte extrait :\n{st.session_state.extracted_text}\n\nQuestion : {user_question}"
                    
                    try:
                        with st.spinner("Gemini réfléchit..."):
                            response = st.session_state.chat.send_message(prompt)
                            st.markdown("### Réponse de Gemini :")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Erreur Gemini : {e}")

if __name__ == "__main__":
    app = Main()
    app.run()