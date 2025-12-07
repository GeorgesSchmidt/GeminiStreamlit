from google import genai
from google.genai import types
import os

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY_Gem"))

chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message("J'ai 2 chiens dans la maison.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)