import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiVisionAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY_IMG")
        
        if not api_key:
            raise ValueError("Clé GOOGLE_API_KEY_IMG manquante dans le .env")
            
        genai.configure(api_key=api_key)
        
        # On utilise un modèle qui figure dans votre liste de diagnostic
        # gemini-2.0-flash est excellent pour l'OCR et très rapide.
        self.model_id = 'gemini-2.0-flash' 
        self.model = genai.GenerativeModel(self.model_id)

    def analyze_pdf(self, file_path: str, prompt: str):
        if not os.path.exists(file_path):
            return "Fichier introuvable."

        try:
            print(f"--- Utilisation du modèle : {self.model_id} ---")
            print(f"--- Envoi du fichier : {os.path.basename(file_path)} ---")
            
            # Étape 1 : Upload du fichier sur l'API
            sample_file = genai.upload_file(path=file_path, mime_type="application/pdf")
            
            # Étape 2 : Analyse
            response = self.model.generate_content([sample_file, prompt])
            
            # Étape 3 : Nettoyage immédiat du fichier sur le cloud
            genai.delete_file(sample_file.name)
            
            return response.text

        except Exception as e:
            return f"Erreur lors de l'analyse : {str(e)}"
        
def main():
    directory = '/users/georgesschmidt/Documents/Medecin'
    paths = os.listdir(directory)
    for path in paths:
        if path.endswith('.pdf'):
            print(path)

if __name__ == "__main__":
    main()
    # agent = GeminiVisionAgent()
    
    # # Chemin vers votre document
    # path = "/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/PDF/AttestationPCAP.pdf"
    
    # # Question précise
    # instruction = "Peux-tu extraire le texte de ce document et me dire de quoi il s'agit ?"
    
    # resultat = agent.analyze_pdf(path, instruction)
    
    # print("\n--- RÉSULTAT ---")
    # print(resultat)