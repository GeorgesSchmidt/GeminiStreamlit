import streamlit as st
import os
import sys
from google import genai
from google.genai import types
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PDFanalysis.analysePDF import ReadPDF


class Main:
    def __init__(self):
        # --- Rendre le client persistant ---
        if "client" not in st.session_state:
            st.session_state.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY_Gem"))

        if "chat" not in st.session_state:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.5-flash"
            )

        self.chat = st.session_state.chat
        self.analyse_file = ReadPDF()

        self.question = ""
        self.path = None
        self.analyse_btn = False


    def afficher_champ_texte(self):
        self.question = st.text_input("ask gemini a question about this (those) images :")


    def afficher_uploader(self):
        self.path = st.file_uploader("Choose a file :", type=['png', 'jpg', 'jpeg'])
        if self.path:
            self.analyse_btn = st.button("Analyser le texte de l’image avec Gemini")


    def afficher_resultats(self):
        # --- Partie question texte ---
        if self.question:
            response = self.chat.send_message(self.question)
            st.write(response.text)

        # --- Partie image ---
        if self.path is not None:
            st.write("Fichier chargé :", self.path.name)
            type_doc = self.path.name.split('.')[-1]

            if type_doc in ['png', 'jpg', 'jpeg']:
                # Lecture OCR
                self.analyse_file.convert_img(self.path)
            elif type == 'pdf':
                self.analyse_file.convert_pdf(self.path)
            self.analyse_file.detect_language()
            self.analyse_file.read_doc()

            st.write("Texte extrait :")
            st.text(self.analyse_file.text)

            # --- Analyse par Gemini ---
            if self.analyse_btn:
                user_question = self.question if self.question else "Please analyze this text: summarize it, explain what it contains, and point out any important information."

                prompt = f"""
                Here is the text extracted from an image:

                {self.analyse_file.text}

                User's question: {user_question}

                """

                response = self.chat.send_message(prompt)
                st.subheader("Gemini Analysis:")
                st.write(response.text)
                    
           
                
                


    def run(self):
        st.title("Gemini analysis")
        self.afficher_champ_texte()
        self.afficher_uploader()
        self.afficher_resultats()


if __name__ == "__main__":
    app = Main()
    app.run()
