# test_agent.py


from google import genai
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from documentAgent import DocumentAgent
from geminiClient import GeminiClient

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY_Gem"))
chat = client.chats.create(model="gemini-2.5-flash")

gemini = GeminiClient(chat)
agent = DocumentAgent(gemini)

path = '/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/TextSamples/sample.txt'
text = open(path).read()
output = agent.run(text)

print(output)
