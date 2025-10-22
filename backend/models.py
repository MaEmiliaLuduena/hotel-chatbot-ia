# Comprobar modelos disponibles con mi API Key
import google.generativeai as genai
genai.configure(api_key='AIzaSyAn7jPjc4fgtlFj6ibmAZAvwXkVHOWSenM')

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)