"""Check available Gemini models"""
import os
import google.generativeai as genai

os.environ['GOOGLE_API_KEY'] = 'AIzaSyBhkZ_krdwjmLISz-xecz7Cmm7eHo6oIAc'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
