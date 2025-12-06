from google import genai
from google.genai import types



client = genai.Client(api_key="AIzaSyCHD6S4PJ5m3nmra_qzNF1sMeAAiPLuNW8")

# Upload the first image
image1_path = "/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/Pics/IMG_1409.jpg"
uploaded_file = client.files.upload(file=image1_path)

# Prepare the second image as inline data
image2_path = "/Users/georgesschmidt/VisualCodeProjects/GemeniTuto/Pics/PICT0190.jpg"
with open(image2_path, 'rb') as f:
    img2_bytes = f.read()

# Create the prompt with text and multiple images
response = client.models.generate_content(

    model="gemini-2.5-flash",
    contents=[
        "Quelles sont les similitudes entre ces 2 images ?",
        uploaded_file,  # Use the uploaded file reference
        types.Part.from_bytes(
            data=img2_bytes,
            mime_type='image/png'
        )
    ]
)

print(response.text)