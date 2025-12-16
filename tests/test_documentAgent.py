import pytest
from unittest.mock import MagicMock

from AgentIA.documentAgent import DocumentAgent

# ------------------------------------------------------------
# Fixture : mock Gemini client
# ------------------------------------------------------------
@pytest.fixture
def mock_gemini():
    mock = MagicMock()
    # mock.send_message().text
    mock.send_message.return_value.text = "FACTURE"
    return mock

@pytest.fixture
def agent(mock_gemini):
    return DocumentAgent(mock_gemini)

# ------------------------------------------------------------
# Tests unitaires
# ------------------------------------------------------------

def test_classify(agent, mock_gemini):
    text = "Voici un texte OCR"
    doc_type = agent.classify(text)

    mock_gemini.send_message.assert_called_once()
    assert doc_type == "facture"  # lowercase du mock
  

def test_choose_mission(agent):
    # types connus
    assert agent.choose_mission("facture") == "Extraire les informations comptables importantes."
    assert agent.choose_mission("cv") == "Extraire le profil et les compétences."
    # type inconnu
    assert agent.choose_mission("xyz") == "Produire un résumé général."

def test_execute(agent, mock_gemini):
    text = "Document de test"
    mission = "Extraire infos"
    mock_gemini.send_message.return_value.text = "Résultat simulé"

    result = agent.execute(text, mission)
    mock_gemini.send_message.assert_called()
    assert result == "Résultat simulé"

def test_run(agent, mock_gemini):
    text = "Texte pour test complet"
    # mock pour classify
    mock_gemini.send_message.return_value.text = "CONTRAT"
    output = agent.run(text)

    assert output["document_type"] == "contrat"
    assert output["mission"] == "Résumer les obligations, risques et points clés."
    assert output["result"] == "CONTRAT"  # valeur renvoyée par execute (mock)
