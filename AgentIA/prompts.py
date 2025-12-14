DOCUMENT_TYPE_PROMPT = """
Tu es un assistant qui classe des documents à partir de leur texte OCR.

TEXTE :
----------------
{document_text}
----------------

Type du document (une seule étiquette) :
facture | contrat | cv | article | courrier | document_technique | inconnu
"""

MISSION_PROMPT = """
Tu es un assistant spécialisé dans l'analyse de documents.

MISSION :
{mission}

DOCUMENT :
----------------
{document_text}
----------------

Réponse claire et structurée.
"""
