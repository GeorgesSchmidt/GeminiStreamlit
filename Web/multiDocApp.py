import streamlit as st
import sys
import os
from dotenv import load_dotenv
from google import genai

# --- Load environment variables ---
load_dotenv()

# --- Ajouter le chemin vers le dossier parent (GemeniTuto) ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from AgentIA.documentAgent import DocumentAgent
from PDFanalysis.analysePDF import ReadPDF


# -----------------------------------------------------------
# Classe pour traiter un document
# -----------------------------------------------------------
class DocumentProcessor:
    def __init__(self, chat_client, max_pages=3):
        self.chat_client = chat_client
        self.max_pages = max_pages

    def process(self, file) -> dict:
        reader = ReadPDF()
        ext = file.name.split('.')[-1].lower()

        if ext in ['png', 'jpg', 'jpeg']:
            reader.convert_img(file)
        elif ext == 'pdf':
            reader.convert_pdf(file)
        else:
            return {"error": "Type non supporté"}

        reader.detect_language()
        reader.read_doc(max_pages=self.max_pages)

        agent = DocumentAgent(self.chat_client)
        return agent.run(reader.text)

# -----------------------------------------------------------
# Classe principale de l'application Streamlit
# -----------------------------------------------------------
class MultiDocumentAgentApp:
    def __init__(self):
        self._init_gemini()
        self.max_pages = 3

    def _init_gemini(self):
        api_key = os.getenv("GOOGLE_API_KEY_Gem")
        if not api_key:
            st.error("❌ Clé API Gemini manquante !")
            st.stop()
        self.client = genai.Client(api_key=api_key)
        self.chat = self.client.chats.create(model="gemini-2.5-flash")

    def run(self):
        st.title("📚 Multi Document Analyzer (Agent POO)")
        st.write("Upload multiple PDFs or images, classify them, summarize and explain why.")

        self.max_pages = st.number_input("Max pages per document for OCR", value=3, min_value=1)

        uploaded_files = st.file_uploader(
            "📤 Upload files",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )

        if uploaded_files:
            processor = DocumentProcessor(self.chat, max_pages=self.max_pages)
            for f in uploaded_files:
                st.subheader(f"📄 {f.name}")
                with st.spinner("Processing..."):
                    output = processor.process(f)

                    if "error" in output:
                        st.error(output["error"])
                        continue

                    st.markdown(f"**Type détecté :** `{output['document_type']}`")
                    st.markdown(f"**Mission :** {output['mission']}")
                    st.subheader("🤖 Résumé et explication :")
                    st.write(output['result'])

# -----------------------------------------------------------
# RUN APP
# -----------------------------------------------------------
if __name__ == "__main__":
    app = MultiDocumentAgentApp()
    app.run()
