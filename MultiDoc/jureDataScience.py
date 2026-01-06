import os
import time
import re
import csv
import google.generativeai as genai
from google.api_core import exceptions
from dotenv import load_dotenv


class GradingFolderAgent:

    OUTPUT_FOLDER = "LaCapsule"

    SYSTEM_PROMPT = """
Tu es juré pédagogique expert en Data Analysis, Data Engineering et Data Science.
Tu évalues des projets d'étudiants avec rigueur, objectivité et justification factuelle.
Tu te bases UNIQUEMENT sur le contenu du PDF fourni.
"""

    TASK_PROMPT = """
Analyse le document PDF fourni et remplis le questionnaire suivant.

RÈGLES :
- Note chaque compétence sur 5
- Indique le niveau : Acquis / Partiellement acquis / Non acquis
- Donne une observation courte et factuelle
- Respecte STRICTEMENT le format demandé
- N'ajoute aucun texte hors format

FORMAT À RESPECTER :

ETUDIANT: {student_name}

BLOC 1 – ANALYSE DES DONNÉES
1. Identification et calcul des KPIs
Note: X/5
Niveau: ...
Observation: ...

2. Analyse des données pour fournir des insights exploitables
Note: X/5
Niveau: ...
Observation: ...

3. Traduction des données en recommandations actionnables
Note: X/5
Niveau: ...
Observation: ...

BLOC 2 – PRÉPARATION ET TRANSFORMATION DES DONNÉES
4. Collecte de données à partir de différentes sources
Note: X/5
Niveau: ...
Observation: ...

5. Nettoyage et préparation des données
Note: X/5
Niveau: ...
Observation: ...

6. Structuration et transformation des données
Note: X/5
Niveau: ...
Observation: ...

7. Mise en place de workflows automatisés
Note: X/5
Niveau: ...
Observation: ...

8. Intégration de données en temps réel
Note: X/5
Niveau: ...
Observation: ...

BLOC 3 – BASES DE DONNÉES
9. Conception et modélisation des bases de données
Note: X/5
Niveau: ...
Observation: ...

10. Administration de la base de données
Note: X/5
Niveau: ...
Observation: ...

11. Manipulation de la base de données
Note: X/5
Niveau: ...
Observation: ...

12. Protection des données personnelles et sécurisation
Note: X/5
Niveau: ...
Observation: ...

BLOC 4 – VISUALISATION ET REPORTING
13. Conception d’un Data Warehouse
Note: X/5
Niveau: ...
Observation: ...

14. Manipulation des données dans un Data Warehouse
Note: X/5
Niveau: ...
Observation: ...

15. Création de visualisations avec des outils BI
Note: X/5
Niveau: ...
Observation: ...

16. Tableaux de bord interactifs
Note: X/5
Niveau: ...
Observation: ...

17. Storytelling data
Note: X/5
Niveau: ...
Observation: ...

BLOC 5 – DATA SCIENCE ET MACHINE LEARNING
18. Exploration et analyse statistique
Note: X/5
Niveau: ...
Observation: ...

19. Préparation des données pour la modélisation
Note: X/5
Niveau: ...
Observation: ...

20. Mise en œuvre de modèles prédictifs
Note: X/5
Niveau: ...
Observation: ...

21. Validation et évaluation des modèles
Note: X/5
Niveau: ...
Observation: ...

22. Méthodologies de data mining
Note: X/5
Niveau: ...
Observation: ...
"""

    def __init__(self):
        load_dotenv()
        "Il faut enregistrer la clef dans ton terminal par export GOOGLE_API_KEY='ta clef ici' "
        api_key = os.getenv("GOOGLE_API_KEY_IMG")

        if not api_key:
            raise ValueError("❌ Clé GOOGLE_API_KEY_IMG absente du fichier .env")

        genai.configure(api_key=api_key)
        # Utilisation de gemini-1.5-flash ou 2.0-flash
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

    def process_folder(self, input_folder: str) -> None:
        if not os.path.isdir(input_folder):
            raise ValueError("❌ Dossier source introuvable")

        pdf_files = sorted(
            f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")
        )

        if not pdf_files:
            print("⚠️ Aucun fichier PDF trouvé.")
            return

        report_text = []
        csv_rows = []

        for filename in pdf_files:
            "Ici le pdf a pour titre le nom de l'élève"
            student_name = os.path.splitext(filename)[0]
            file_path = os.path.join(input_folder, filename)

            print(f"📄 Analyse en cours : {filename}...")

            try:
                # 1. Upload du fichier
                uploaded = genai.upload_file(path=file_path, mime_type="application/pdf")
                prompt = self.TASK_PROMPT.format(student_name=student_name)

                # 2. Tentative de génération avec gestion du quota (Retry logic)
                result_text = self._generate_with_retry(uploaded, prompt)

                if result_text:
                    # Nettoyage fichier après succès
                    genai.delete_file(uploaded.name)
                    
                    report_text.append(f"SOURCE : {filename}\n{result_text}\n{'='*60}")
                    
                    parsed = self._parse_response(result_text, student_name)
                    if parsed:
                        csv_rows.append(parsed)
                    
                    # Petite pause de sécurité entre deux fichiers
                    time.sleep(5) 

            except Exception as e:
                print(f"❌ Erreur critique sur {filename} : {e}")

        self._save_outputs(report_text, csv_rows)
        print("\n✅ Toutes les analyses sont terminées.")

    def _generate_with_retry(self, uploaded_file, prompt, max_retries=3):
        "Quand le pdf est trop volumineux, le quota de connexion avec l'agent est atteint et on obtient une erreur 429."
        """Tente de générer le contenu et attend en cas d'erreur 429."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    [self.SYSTEM_PROMPT, uploaded_file, prompt]
                )
                return response.text.strip()
            except exceptions.ResourceExhausted:
                wait_time = 60  # On attend 1 minute si le quota est plein
                print(f"⚠️ Quota atteint (429). Pause de {wait_time}s... (Tentative {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            except Exception as e:
                print(f"❌ Erreur API : {e}")
                break
        return None

    def _parse_response(self, text: str, default_name: str) -> dict | None:
        """
        Extrait proprement le nom et la note finale via Regex.
        """
        try:
            # Recherche de la note finale (ex: NOTE_FINALE: 15/20 ou 15)
            note_match = re.search(r"NOTE_FINALE:\s*([\d.,]+)", text)
            note = note_match.group(1) if note_match else "N/A"

            # Recherche du nom de l'étudiant
            name_match = re.search(r"ETUDIANT:\s*(.*)", text)
            name = name_match.group(1).strip() if name_match else default_name

            return {"Nom": name, "Note": note}
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction des données : {e}")
            return {"Nom": default_name, "Note": "Erreur"}

    def _save_outputs(self, report: list[str], csv_rows: list[dict]) -> None:
        txt_path = os.path.join(self.OUTPUT_FOLDER, "NotesEtCritiques.txt")
        csv_path = os.path.join(self.OUTPUT_FOLDER, "Notes.csv")

        if report:
            with open(txt_path, "a", encoding="utf-8") as f:
                f.write("\n\n".join(report))

        if csv_rows:
            with open(csv_path, "a", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["Nom", "Note"])
                writer.writeheader()
                writer.writerows(csv_rows)

        print(f"\n📍 Rapport texte : {txt_path}")
        print(f"📍 Fichier CSV   : {csv_path}")

# --- LANCEMENT ---
if __name__ == "__main__":
    agent = GradingFolderAgent()
    "Path = lien vers le dossier qui contient les pdf à lire"
    source = "/Users/georgesschmidt/Documents/LaCapsuleJanvier2026/mardi6"
    agent.process_folder(source)
