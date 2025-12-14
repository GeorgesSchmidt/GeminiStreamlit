import streamlit as st
import os
import sys
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
        self.question = st.text_input("💬 Ask Gemini a question about the uploaded image:")

    def afficher_uploader(self):
        """File uploader UI."""
        self.path = st.file_uploader("📤 Upload an image", type=['png', 'jpg', 'jpeg', 'pdf'])
        if self.path:
            self.analyse_btn = st.button("🔍 Analyze extracted text with Gemini")

    # -----------------------------------------------------------
    # Core Logic
    # -----------------------------------------------------------
    def afficher_resultats(self):
        """Display results from Gemini based on user input or uploaded file."""

        # --- TEXT QUESTION PART ---
        if self.question and len(self.analyse_file.text) > 0:
            response = self.chat.send_message(self.question)
            st.subheader("💡 Gemini Answer:")
            st.write(response.text)

        # --- IMAGE ANALYSIS PART ---
        if self.path is not None:
            st.subheader("📄 Uploaded file:")
            st.write(self.path.name)

            extension = self.path.name.split('.')[-1].lower()

            # Extract text depending on file type
            if extension in ['png', 'jpg', 'jpeg']:
                self.analyse_file.convert_img(self.path)
            elif extension == "pdf":
                self.analyse_file.convert_pdf(self.path)
            else:
                st.error("❌ Unsupported file type.")
                return

            # OCR + Language detection + Read
            self.analyse_file.detect_language()
            self.analyse_file.read_doc()

            # Display extracted text
            st.subheader("📝 Extracted Text:")
            st.text(self.analyse_file.text)

            # --- Gemini Analysis ---
            if self.analyse_btn:
                user_question = (
                    self.question if self.question
                    else "Please analyze this text: summarize it, explain what it contains, and highlight key points."
                )

                prompt = f"""
                Here is the text extracted from the image:

                {self.analyse_file.text}

                User's question:
                {user_question}
                """

                response = self.chat.send_message(prompt)

                st.subheader("🤖 Gemini Analysis:")
                st.write(response.text)

    # -----------------------------------------------------------
    # RUN APP
    # -----------------------------------------------------------
    def run(self):
        st.title("📘 Gemini Image/Text Analyzer")
        st.write("Upload an image, extract its content, and ask Gemini anything about it.")

        self.afficher_uploader()
        self.afficher_champ_texte()
        self.afficher_resultats()


# -----------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------
if __name__ == "__main__":
    app = Main()
    app.run()
