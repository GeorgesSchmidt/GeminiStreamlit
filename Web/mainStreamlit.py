import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from google import genai

# --- Load environment variables ---
load_dotenv()

# --- Custom module import ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PDFanalysis.analysePDF import ReadPDF


class Main:
    """
    Streamlit application for:
    - Uploading images
    - Extracting text via custom OCR module
    - Asking questions to Gemini
    - Analyzing extracted text using Gemini
    """

    def __init__(self):
        self._init_gemini_client()
        self.chat = st.session_state.chat

        self.analyse_file = ReadPDF()
        self.question = ""
        self.path = None
        self.analyse_btn = False

    # -----------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------
    def _init_gemini_client(self):
        """Initialize Gemini client and persistent chat session."""
        api_key = os.getenv("GOOGLE_API_KEY_Gem")

        if not api_key:
            st.error("❌ ERROR: Missing environment variable `GOOGLE_API_KEY_Gem`.")
            st.stop()

        if "client" not in st.session_state:
            st.session_state.client = genai.Client(api_key=api_key)

        if "chat" not in st.session_state:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.5-flash"
            )

    # -----------------------------------------------------------
    # UI Components
    # -----------------------------------------------------------
    def afficher_champ_texte(self):
        """Text input for user question."""
        self.question = st.text_input("💬 Ask Gemini a question about text:")

    def afficher_uploader(self):
        """File uploader UI."""
        self.path = st.file_uploader("📤 Upload an image", type=['png', 'jpg', 'jpeg', 'pdf'])
        if self.path is not None:
            st.subheader("📄 Uploaded file:")
            st.write(self.path.name)
            #self.analyse_btn = st.button("🔍 Analyze extracted text with Gemini")
            self.afficher_resultats()

    # -----------------------------------------------------------
    # Core Logic
    # -----------------------------------------------------------
    def afficher_resultats(self):
        start_time = time.time()
        extension = self.path.name.split('.')[-1].lower()

        # OCR
        if extension in ['png', 'jpg', 'jpeg']:
            self.analyse_file.convert_img(self.path)
        elif extension == "pdf":
            self.analyse_file.convert_pdf(self.path)
        else:
            st.error("❌ Unsupported file type.")
            return

        self.analyse_file.detect_language()
        self.analyse_file.read_doc()
        end_time = time.time()
        duration = int(end_time - start_time)

        # Affichage OCR
        st.subheader("📝 Extracted Text:")
        st.text_area("Text from document:", self.analyse_file.text, height=300)
        st.text(f'Document read in {duration} s')
        st.text(f'The text language: {self.analyse_file.lang}')
        st.text(f'Word count: {len(self.analyse_file.text.split())}')

        # Interaction Gemini
        self.question = st.text_input("💬 Ask Gemini a question about this text:")
        self.analyse_btn = st.button("🔍 Get Gemini response")

        if self.analyse_btn:
            user_question = (
                self.question
                if self.question
                else "Please analyze this text: summarize and highlight key points."
            )

            prompt = f"""
            Text extracted from document:

            {self.analyse_file.text}

            User question: {user_question}
            """

            try:
                response = self.chat.send_message(prompt)
                st.subheader("🤖 Gemini Analysis:")
                st.text_area("Gemini response:", response.text, height=300)
            except Exception as e:
                st.error(f"⚠️ Gemini is temporarily unavailable: {e}")


    # -----------------------------------------------------------
    # RUN APP
    # -----------------------------------------------------------
    def run(self):
        st.title("📘 Gemini Image/Text Analyzer")
        st.write("Upload an image containing text or a pdf document, this program extract the text and you can ask gemini about this text.")
        st.write('OCR detection take about 32 s for a single page document up to 6 minutes for a 25 pages, please wait')

        self.afficher_uploader()
        # self.afficher_champ_texte()
        # self.afficher_resultats()


# -----------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------
if __name__ == "__main__":
    app = Main()
    app.run()
