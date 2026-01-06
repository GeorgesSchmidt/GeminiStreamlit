import streamlit as st
import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURATION DES CHEMINS ---
# On récupère le chemin absolu du dossier où se trouve ce script (Web/)
CURRENT_DIR = Path(__file__).parent.absolute()
# On récupère le chemin du dossier racine (le parent de Web/)
ROOT_DIR = CURRENT_DIR.parent.absolute()

# On ajoute ROOT_DIR au path pour pouvoir importer jureDataScience
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Import direct maintenant que le path est configuré
try:
    from MultiDoc.jureDataScience import GradingFolderAgent
except ImportError as e:
    st.error(f"Impossible d'importer l'agent : {e}")
    st.stop()

class StreamlitInterface:
    def __init__(self):
        self._load_env()
        self.setup_page()
        self._init_agent()

    def _load_env(self):
        """Cherche le .env à la racine du projet"""
        env_path = ROOT_DIR / ".env"
        load_dotenv(dotenv_path=env_path)

    def _init_agent(self):
        """Initialise ton agent en vérifiant la clé API"""
        if 'agent_instance' not in st.session_state:
            api_key = os.getenv("GOOGLE_API_KEY_IMG")
            
            if not api_key:
                st.error("❌ Clé GOOGLE_API_KEY introuvable.")
                st.info(f"Recherchée dans : {ROOT_DIR / '.env'}")
                st.stop()
            
            try:
                st.session_state.agent_instance = GradingFolderAgent()
            except Exception as e:
                st.error(f"Erreur lors de l'instanciation de l'agent : {e}")
                st.stop()
        
        self.agent = st.session_state.agent_instance

    def setup_page(self):
        st.set_page_config(page_title="IA Grading Dashboard", layout="wide")
        st.title("🎓 Interface Juré (Multi-dossiers)")

    def run(self):
        uploaded_file = st.file_uploader("Charger un projet étudiant (PDF)", type="pdf")

        if uploaded_file:
            if st.button("Lancer l'Analyse"):
                self.process_upload(uploaded_file)

    def process_upload(self, uploaded_file):
        # Utilisation d'un dossier temporaire pour simuler le dossier source de ton agent
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Analyse en cours... Ton agent gère les pauses (429)."):
                try:
                    # Exécution de la méthode originale de ta classe
                    self.agent.process_folder(tmp_dir)
                    st.success("Analyse terminée avec succès.")
                    self.display_results()
                except Exception as e:
                    st.error(f"Erreur durant l'analyse : {e}")

    def display_results(self):
        # Chemin vers le dossier de sortie créé par ton agent
        # Par défaut, ton agent écrit dans "LaCapsule" à la racine de l'exécution
        txt_path = os.path.join("LaCapsule", "NotesEtCritiques.txt")
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.subheader("Dernier rapport généré")
            st.text_area("Notes et Critiques", value=content, height=400)
        else:
            st.warning("Fichier de sortie introuvable.")

if __name__ == "__main__":
    app = StreamlitInterface()
    app.run()