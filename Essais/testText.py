from google import genai
from google.genai import types

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyCFo2sGw_-pYm_Rar3pmdDDVNIlZ_6mfog")

chat = client.chats.create(model="gemini-2.5-flash")

response = chat.send_message("J'ai 2 chiens dans la maison.")
print(response.text)

response = chat.send_message("How many paws are in my house?")
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)