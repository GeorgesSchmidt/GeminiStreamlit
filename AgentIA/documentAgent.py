import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from .prompts import *


class DocumentAgent:
    def __init__(self, gemini_client):
        self.gemini = gemini_client

        self.missions = {
            "facture": "Extraire les informations comptables importantes.",
            "contrat": "Résumer les obligations, risques et points clés.",
            "cv": "Extraire le profil et les compétences.",
            "article": "Produire un résumé structuré.",
            "courrier": "Expliquer l'objet et les actions attendues.",
            "document_technique": "Expliquer le but et les points techniques.",
            "inconnu": "Produire un résumé général."
        }

    def classify(self, text: str) -> str:
        prompt = DOCUMENT_TYPE_PROMPT.format(document_text=text)
        return self.gemini.send_message(prompt).text.lower()


    def choose_mission(self, doc_type: str) -> str:
        return self.missions.get(doc_type, self.missions["inconnu"])

    def execute(self, text: str, mission: str) -> str:
        prompt = MISSION_PROMPT.format(mission=mission, document_text=text)
        return self.gemini.send_message(prompt).text

    def run(self, text: str) -> dict:
        doc_type = self.classify(text)
        mission = self.choose_mission(doc_type)
        result = self.execute(text, mission)

        return {
            "document_type": doc_type,
            "mission": mission,
            "result": result
        }
