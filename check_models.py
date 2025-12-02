"""Check available Gemini models"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file (never hardcode keys!)
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment. Add to .env file.")

genai.configure(api_key=api_key)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
