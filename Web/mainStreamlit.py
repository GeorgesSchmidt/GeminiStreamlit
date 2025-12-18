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
    def __init__(self):
        self._init_gemini_client()
        # Initialize OCR object in session state
        if "analyse_file" not in st.session_state:
            st.session_state.analyse_file = ReadPDF()
        
        # Store extracted text to avoid re-running OCR unnecessarily
        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = None
            st.session_state.detected_lang = "Unknown"

    def _init_gemini_client(self):
        """Securely initialize Gemini client."""
        # Use st.secrets for production, os.getenv for local development
        api_key = st.secrets.get("GOOGLE_API_KEY_Gem") or os.getenv("GOOGLE_API_KEY_Gem")

        if not api_key:
            st.error("❌ ERROR: Missing API Key (GOOGLE_API_KEY_Gem).")
            st.stop()

        if "client" not in st.session_state:
            st.session_state.client = genai.Client(api_key=api_key)

        if "chat" not in st.session_state:
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-2.0-flash" 
            )

    def run_ocr_process(self, uploaded_file):
        """Execute OCR and store the result in session_state."""
        start_time = time.time()
        extension = uploaded_file.name.split('.')[-1].lower()
        
        reader = st.session_state.analyse_file

        with st.spinner("🔍 OCR in progress... Please wait."):
            if extension in ['png', 'jpg', 'jpeg']:
                reader.convert_img(uploaded_file)
            elif extension == "pdf":
                reader.convert_pdf(uploaded_file)
            
            # Check if method exists before calling
            if hasattr(reader, 'detect_language'):
                reader.detect_language()
            
            reader.read_doc()
            
            # Save to state
            st.session_state.extracted_text = reader.text
            st.session_state.detected_lang = reader.lang
            st.session_state.duration = int(time.time() - start_time)

    def run(self):
        st.title("📘 Gemini Image/Text Analyzer")
        st.info("OCR takes about 30s per page. Please stay on this page after uploading.")

        uploaded_file = st.file_uploader("📤 Upload an image or PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

        if uploaded_file:
            # If a new file is uploaded, reset the previous extraction
            if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
                st.session_state.last_uploaded = uploaded_file.name
                st.session_state.extracted_text = None

            # Button to trigger OCR
            if st.session_state.extracted_text is None:
                if st.button("🚀 Start Text Extraction"):
                    self.run_ocr_process(uploaded_file)
                    st.rerun()

            # Display results and Gemini interface if text has been extracted
            if st.session_state.extracted_text:
                st.subheader("📝 Extracted Text:")
                st.text_area("Result:", st.session_state.extracted_text, height=250)
                
                col1, col2 = st.columns(2)
                col1.write(f"⏱ Processing Time: {st.session_state.get('duration', 0)}s")
                col2.write(f"🌍 Detected Language: {st.session_state.detected_lang}")

                st.divider()

                # Gemini Interaction
                st.subheader("🤖 Ask Gemini")
                user_question = st.text_input("Ask a question about the document:", key="gemini_q")
                
                if st.button("🔍 Ask Gemini"):
                    if not user_question:
                        user_question = "Please provide a concise summary of this text."
                    
                    prompt = f"Extracted Text:\n{st.session_state.extracted_text}\n\nUser Question: {user_question}"
                    
                    try:
                        with st.spinner("Gemini is thinking..."):
                            response = st.session_state.chat.send_message(prompt)
                            st.markdown("### Gemini's Response:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Gemini Error: {e}")

if __name__ == "__main__":
    app = Main()
    app.run()