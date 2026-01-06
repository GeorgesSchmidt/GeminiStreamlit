import os
import google.generativeai as genai
from dotenv import load_dotenv

class HealthFolderAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY_IMG")
        if not api_key:
            raise ValueError("Clé GOOGLE_API_KEY_IMG manquante dans le .env")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Création automatique du dossier de sortie
        self.output_folder = "Resultats"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"📁 Dossier '{self.output_folder}' créé.")

    def process_folder(self, input_folder: str):
        # Lister les PDF
        files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
        files.sort()

        if not files:
            print("Aucun fichier PDF trouvé dans le dossier source.")
            return

        full_history = "--- HISTORIQUE MÉDICAL CHRONOLOGIQUE ---\n\n"
        csv_data_accumulator = "" # Pour accumuler les lignes CSV brutes

        for filename in files:
            path = os.path.join(input_folder, filename)
            print(f"🔍 Analyse de : {filename}...")

            try:
                # 1. Upload temporaire
                doc = genai.upload_file(path=path, mime_type="application/pdf")

                # 2. Analyse mixte (Classification + Extraction)
                prompt = """
                Tu es juré en data science. Tu dois lire les pdf qui te sont confiés et les noter sur une échelle entre 0 et 20.
                Dans le fichier NotesEtCritiques tu marque le nom de l'élève qui est le titre du pdf, tu donnes la note et tu écris une appréciation positive et une négative.
                
                
                """

                response = self.model.generate_content([doc, prompt])
                res_text = response.text
                genai.delete_file(doc.name)

                # 3. Répartition vers l'historique texte
                full_history += f"SOURCE : {filename}\n{res_text}\n"
                full_history += "="*60 + "\n"

                # 4. Récupération spécifique des lignes CSV
                if "---CSV---" in res_text:
                    parts = res_text.split("---CSV---")
                    csv_part = parts[1].strip()
                    if len(csv_part) > 10: # Évite les blocs vides
                        csv_data_accumulator += csv_part + "\n"

            except Exception as e:
                print(f"❌ Erreur sur {filename} : {e}")

        # --- SAUVEGARDE DANS LE DOSSIER 'Resultats' ---
        
        txt_path = os.path.join(self.output_folder, "NotesEtcritiques.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_history)

        # csv_path = os.path.join(self.output_folder, "courbes_analyses.csv")
        # with open(csv_path, "w", encoding="utf-8") as f:
        #     f.write("Date,Paramètre,Valeur,Unité\n") # En-tête
        #     # Nettoyage minimal pour enlever d'éventuels backticks Markdown
        #     clean_csv = csv_data_accumulator.replace('```csv', '').replace('```', '').strip()
        #     f.write(clean_csv)

        print(f"\n✅ Analyse terminée.")
        print(f"📍 Rapport texte : {txt_path}")
        #print(f"📍 Données CSV   : {csv_path}")

# --- LANCEMENT ---
if __name__ == "__main__":
    agent = HealthFolderAgent()
    # Modifiez le chemin source si nécessaire
    #source = "/Users/georgesschmidt/Documents/Medecin"
    source = "/Users/georgesschmidt/Documents/LaCapsuleJanvier2026"
    agent.process_folder(source)